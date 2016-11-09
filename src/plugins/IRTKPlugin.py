# Eidolon Biomedical Framework
# Copyright (C) 2016 Eric Kerfoot, King's College London, all rights reserved
# 
# This file is part of Eidolon.
#
# Eidolon is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Eidolon is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program (LICENSE.txt).  If not, see <http://www.gnu.org/licenses/>

from eidolon import *

from VTKPlugin import DatasetTypes,VTKProps
from SegmentPlugin import DatafileParams,SegSceneObject,SegmentTypes

from mtServerForm import Ui_mtServerForm
import sys
import glob
import subprocess
import socket
import SocketServer
import pickle
import inspect
import traceback
import shutil
import itertools 

from contextlib import closing

from numpy.fft import fftn,ifftn,fftshift,ifftshift


def isPositiveDefinite(mat):
	'''Returns True if `mat' is a positive definite matrix (ie. all positive eigenvalues).'''
	return np.all(np.linalg.eigvals(mat) >= 0)


def fillMatrix(nmat,rmat):
	w,h=nmat.shape
	for n in range(min(h,rmat.n())):
		rmat.setRow(n,*map(float,nmat[:,n]))


def imgfft3d(mat,coresize,revert):
	xmax,ymax,zmax=mat.shape
	xs = int(math.floor(xmax/2))
	ys = int(math.floor(ymax/2))
	zs = int(math.floor(zmax/2))

	x,y,z =np.meshgrid(range(-ys,ys+1),range(-xs,xs+1),range(-zs,zs+1))

	dist=np.sqrt(x**2+y**2+z**2)
	c=(dist < math.sqrt(3*(coresize**2)))
	if revert:
		c=(c==0)

	mat1 = fftshift(fftn(mat))
	mat2=mat1*c
	return ifftn(ifftshift(mat2))


def detagImage(obj,coresize,revert=False):
	vinds=obj.getVolumeStacks()
	width,height,depth=obj.maxcols,obj.maxrows,len(vinds[0])
	xred=1-width%2
	yred=1-height%2
	zred=1-depth%2

	for inds in vinds:
		img=np.ndarray((width,height,depth),np.float64)
		# read the image stack into the array
		for d,ind in enumerate(inds):
			img[:,:,d]=matrixToArray(obj.images[ind].img,np.float64).T

		# ensure that the image array has odd dimensions
		if xred!=0 or yred!=0 or zred!=0:
			img=img[:width-xred,:height-yred,:depth-zred]

		# apply the FFT shift operation
		img1=imgfft3d(img,coresize,revert)
		img1=img1.real

		# read the array back into the images
		for d,ind in enumerate(inds):
			obj.images[ind].img.fill(0)
			if d<(depth-zred):
				fillMatrix(img1[:,:,d],obj.images[ind].img)


@concurrent
def applyMotionTrackRange(process,exefile,cwd,isInvert,filelists):
	results=[]
	for i,(infile,outfile,doffile,ttime) in enumerate(filelists):
		args=[infile,outfile,'-dofin',doffile]

		if isInvert: # invert the transformation
			args.append('-invert')

		if ttime>=0: # timestep selection
			args+=['-time',str(ttime)]

		r=execBatchProgram(exefile,*args,cwd=cwd)
		results.append(r)
		process.setProgress(i+1)

	return results
	

@taskroutine('Applying Transformation')
def applyMotionTrackTask(exefile,cwd,isInvert,filelists,task=None):
	results=applyMotionTrackRange(len(filelists),0,task,exefile,cwd,isInvert,filelists,partitionArgs=(filelists,))
	checkResultMap(results)

InterpTypes=enum(
	('Linear','-linear'),
	('Bezier Spline','-bspline'),
	('Cubic Spline','-cspline'),
	('Truncated Sinc','-sinc'),
	('Shape Based','-sbased'),
	('Gaussian','-gaussian sigma')
)


ServerMsgs=enum(
	('OK',(),'OK Server Response; no values'),
	('Except',(Exception,str),'Exception from Server; exception value, stack trace string info'),
	('Stat',(int,),'Status Request for Job; Job ID value'),
	('RStat',(int,int,int,str),'Status Response; process exit code (None if still running), # of files so far, total # of files, job dir'),
	('StartMotionTrack',(bool,str,str,str,str,float,int,str),'Sending motion track job to server;true if data is file path, file blob otherwise, track file,mask file, param filename, directory name, adaptive, # of TS, root directory'),
	('StartTSFFD',(str,str,str,str),'Sending compute TSFFD job to server; track directory, track filename (not used), mask filename, par file'),
	('RStart',(int,),'Job Send Response; Job ID value'),
	('GetResult',(int,bool),'Get job results; job ID value, true if absolute file paths are requested'),
	('RGetResult',(list,),'Returned job results; list of file paths or file data blobs'),
	('Check',(),'Request the username of whoever started the server; empty'),
	('RCheck',(str,),'Username response; username string'),
	('Kill',(int,),'Job kill command; Job ID value'),
	('RKill',(bool,),'Job kill response; True if successful, False if job was not running'),
	valtype=(tuple,str),
	doc='Server request and response messages, containing the types of the arguments and a description'
)


JobMetaValues=enum('pid','rootdir','numtimesteps','trackfile','maskfile','paramfile','adaptive','resultcode','startdate')


class IRTKPluginMixin(object):
	def init(self,plugid,win,mgr):
		self.Nifti=mgr.getPlugin('Nifti')
		self.Dicom=mgr.getPlugin('Dicom')
		self.Meta=mgr.getPlugin('MetaImg')
		self.Slice=mgr.getPlugin('SlicePlugin')
		self.VTK=mgr.getPlugin('VTK')
		self.CHeart=mgr.getPlugin('CHeart')
		self.Plot=mgr.getPlugin('Plot')
		self.Segment=mgr.getPlugin('Segment')

		self.serverdir=os.path.join(getVizDir(),'motion')
		self.irtkdir=os.path.join(getVizDir(),'EidolonLibs','IRTK')

		self.fixshort=os.path.join(self.irtkdir,'fixshort.txt')
		self.tsffd=os.path.join(self.irtkdir,'tsffd.par')
		self.patient1e4=os.path.join(self.irtkdir,'patient_lambda1-1e-4.txt')
		self.patient1e6=os.path.join(self.irtkdir,'patient_lambda1-1e-6.txt')
		self.nreg_default=os.path.join(self.irtkdir,'nreg_default.txt')
		self.gpu_nreg_default=os.path.join(self.irtkdir,'gpu_nreg_cc_L3_CP40x40x40_l10.cfg')

		self.exesuffix=''
		if isWindows:
			self.exesuffix='.exe'
		elif isLinux:
			self.exesuffix='.bin'

		# by default setup the IRTK executable paths to be those that come with the visualizer
		localirtkpath=lambda i:os.path.join(self.irtkdir,i)+self.exesuffix
		self.irtkpath=localirtkpath
		
		# if the system-installed IRTK is present, use it instead if present
		if isLinux and mgr.conf.get(platformID,'usesystemirtk').lower()!='false' and os.path.exists('/usr/bin/irtk-rreg'):
			self.irtkpath=lambda i:('/usr/bin/irtk-'+i) if os.path.exists('/usr/bin/irtk-'+i) else localirtkpath(i)

		self.spatialcorrect=self.irtkpath('spatial_correct')
		self.rreg=self.irtkpath('rreg')
		self.headertool=self.irtkpath('headertool')
		#self.resample=self.irtkpath('resample')
		#self.makesequence=self.irtkpath('makesequence')
		#self.combineimages=self.irtkpath('combineimages')
		self.motiontrack=self.irtkpath('motiontrackmultimage')
		self.computetsffd=self.irtkpath('computeTSFFD')
		self.enlarge=self.irtkpath('enlarge_image')
		self.transformation=self.irtkpath('transformation')
		self.ptransformation=self.irtkpath('ptransformation')
		self.region=self.irtkpath('region')
		#self.mcubes=self.irtkpath('mcubes')
		self.nreg=self.irtkpath('nreg')
		self.gpu_nreg=self.irtkpath('gpu_nreg') # not part of IRTK

	def getCWD(self):
		pass

	def getNiftiFile(self,name):
		'''Get the NIfTI file in the current context starting with `name', '.nii' is appended to the filename.'''
		return self.getLocalFile(ensureExt(name,'.nii'))

	def getLogFile(self,name):
		'''Get the log file in the current context starting with `name', '.log' is appended to the filename if not already present.'''
		return self.getLocalFile(ensureExt(name,'.log'))

	def getLocalFile(self,name):
		'''Get a file with name `name' in the current context (ie. project directory).'''
		pass

	def getTrackingDirs(self,root=None):
		root=root or self.getLocalFile('.')
		result=[]
		for d in glob.glob(root+'/*'):
			if os.path.isdir(d) and glob.glob(d+'/*.dof.gz'):
				result.append(os.path.abspath(d))

		return result

	def addObject(self,obj):
		'''
		Add an object to the current context (ie. project). If the object is already present, this method should still
		succeed but still do the internal bookkeeping operations needed (ie. save the project).
		'''
		pass

	def loadNiftiFiles(self,filenames):
		'''
		Loads the given NIfTI file paths. The argument `filenames' can be a list of paths, or a Future returning such
		a list. The result value is a Future which eventually will hold the loaded ImageSceneObject instances.
		'''
		pass

	def getUniqueShortName(self,*comps,**kwargs):
		return self.getUniqueObjName(createShortName(*comps,**kwargs))

	def getUniqueObjName(self,name):
		'''Returns an object name guaranteed to be unique and not overwrite an existing file in the current context when saved.'''
		filenames=[splitPathExt(i)[1] for i in glob.glob(self.getLocalFile('*'))]
		objnames=[o.getName() for o in self.mgr.enumSceneObjects()]
		return uniqueStr(name,filenames+objnames)
		
	def getUniqueLocalFile(self,name):
		_,name,ext=splitPathExt(name)
		return self.getLocalFile(self.getUniqueObjName(name)+ext)

	def getServerAddrPort(self):
		'''Returns the server address and port, default is ('localhost',15000).'''
		return 'localhost',15000

	def setServerAddrPort(self,addr,port):
		'''Set the server address and port, setting a value as None will keep existing value.'''
		pass

	def _removeNamedObjs(self,*names):
		objs=[o for o in self.mgr.enumSceneObjects() if o.getName() in names]
		for o in objs:
			self.mgr.removeSceneObject(o)

	def saveToNifti(self,objs,setObjArgs=False):
		f=Future()
		@taskroutine('Converting Image Object(s) to NIfTI')
		def _convertTask(objs,setObjArgs,task=None):
			with f:
				filenames=[]

				for obj in objs:
					obj=Future.get(obj)

					filename=self.getNiftiFile(getValidFilename(obj.getName()))
					printFlush('Saving',filename)
					self.Nifti.saveImage(filename,obj,setObjArgs)
					filenames.append(filename)

				f.setObject(filenames)

		return self.mgr.runTasks(_convertTask(objs,setObjArgs),f)

	def _checkProgramTask(self,result):
		@taskroutine('Checking Program Results')
		def _check(result,task=None):
			result=Future.get(result)

			if result==None:
				raise Exception,'None result from program'
			elif isinstance(result,Exception):
				raise result
			elif result[0]!=0:
				self.mgr.showMsg('The program operation failed (Exit code: %i)'%result[0],'Operation Failed',result[1])
				if task:
					task.flushQueue=True

		self.mgr.runTasks(_check(result))

	def correctNiftiParams(self,sourceobj,destfile,makeProspective=False):
		'''
		Corrects the parameters in the NIfTI file `destfile' with those in the ImageSceneObject or filename `sourceobj'.
		IRTK munges timestep values amongst other things so use this to reset them to what they were in the original.
		If `makeProspective' is True then half of the average difference between timesteps is added to each time.
		'''
		@taskroutine('Correcting NIfTI Header')
		def _correct(sourceobj,destfile,makeProspective,task):
			if isinstance(sourceobj,str):
				sourceobj=self.findObject(sourceobj,False) or self.Nifti.loadImage(sourceobj)

			destobj=self.Nifti.loadImage(destfile)

			timesteps=sourceobj.getTimestepList()
			if makeProspective:
				value=avgspan(timesteps)/2
				timesteps=[ts+value for ts in timesteps]

			destobj.setTimestepList(timesteps)

			self.Nifti.saveObject(destobj,destfile,True)

		self.mgr.runTasks(_correct(sourceobj,destfile,makeProspective))

	def applyHeaderTool(self,inname,outname,doffile,cwd,correctNifti=True):
		logfile=self.getLogFile('headertool.log')
		f=self.mgr.execBatchProgramTask(self.headertool,inname,outname,'-dofin',doffile,logfile=logfile,cwd=cwd)
		self._checkProgramTask(f)

		if correctNifti:
			self.correctNiftiParams(inname,outname)

		return f

	def load3DTagSeries(self,tagobj,makeProspective,loadPlanes=False,makeDetag=True,spacing=vec3(1),tryFix=True):
		'''
		Load the 3D TAG image series and process it into a time-dependent volume combining the 3 magnitude orientations.
		This assumes `tagobj' contains images for 3 orientations in an overlapping volume, with phase and magnitude
		volumes for each orientation and timestep. This ignores the phase images which are assumed to have negative
		minimum image values, while the magnitude images should have 0 as the minimum value.
		'''
		f=Future()
		@taskroutine('Generating Tagged and Detagged Image Series')
		def _loadtags(tagobj,makeProspective,loadPlanes,makeDetag,spacing,tryFix,task):
			with f:
				tagged=self.getUniqueObjName('tagged3d')
				detagged=self.getUniqueObjName('detag3d')
				coresize=4
				objs=[]
				loadnames=[]
				
				tagobj=Future.get(tagobj)
				#magimgs=[i for i in tagobj.images if i.imgmin>=0] # magnitude images only, remove phase images
				magimgs=tagobj.images[:len(tagobj.images)/2] # magnitude images only, remove phase images assuming these are the last half of the series
				tagobj=ImageSceneObject('tempobj',tagobj.source,magimgs,tagobj.plugin)
				
				tsinds=tagobj.getTimestepIndices()
				tso=tagobj.getOrientMap()
				ts=[t[0] for t in tsinds]
				
				if len(tso)!=3:
					raise IOError,'Should have 3 orientations: %r'%tso.keys()
					
				#isorthos=[o1.isOrthogonalTo(o2) or o1.isOrthogonalTo(o3) for o1,o2,o3 in successive(tso,3,True)]
				
				if makeProspective: # prospective timing, add half the average difference between timesteps to each timestep
					value=avgspan(ts)/2
					ts=[t+value for t in ts]
					
				# For each of the 3 orientations, take the magnitude images for that orientation and create a temporary 
				# image object. Each object will then have all the images over time for one of the tag orientations.
				for o,olist in enumerate(tso.values()):
					oimages=indexList(olist,magimgs)
					plane=ImageSceneObject('%s_plane%i'%(tagged,o),tagobj.source,oimages,self,True)
					plane.setTimestepList(ts)
					plane.calculateAABB(True)
					objs.append(plane)
					
#					# TODO: Sort out the definite positive issue to remove or otherwise handle bad tag volumes	
#					# NOTE: Sometimes a positive definite image is in the correct position, this isn't a reliable mechanism for 
#					#       identifying bad tag series anymore	
#					mat=np.matrix(plane.images[0].orientation.toMatrix())
#					# flip volume if its matrix is bogus
#					if tryFix and isPositiveDefinite(mat):
#						for i in plane.images:
#							sx,sy=i.spacing
#							i.spacing=(sx,-sy)
#							i.calculateDimensions()
#							
#						plane.calculateAABB(True)
					
				if tryFix:
					bbs=[o.aabb for o in objs]
					#avgcenter=avg((b.center for b in bbs),vec3())
					dist,mid=min((b1.center.distTo(b2.center),(b1.center+b2.center)*0.5) for b1,b2 in itertools.product(bbs,repeat=2) if b1 is not b2)
					
					for bb,o in zip(bbs,objs):
						#if bb.center.distTo(avgcenter)>bb.radius/3:
						if bb.center.distTo(mid)>dist*3:
							for i in o.images:
								sx,sy=i.spacing
								i.spacing=(sx,-sy)
								i.calculateDimensions()
								
							o.calculateAABB(True)
							break
				
				# create an image within the plane-aligned series, disregarding those volumes that may be in an incorrect orientation
				tag=tagobj.plugin.createIntersectObject(tagged,objs,len(ts),spacing)				
				tag.setTimestepList(ts)

				mergefunc='(prod(v/100.0 for v in vals)**(1.0/len(vals)))*100.0'
				mergeImages(objs,tag,mergefunc,task) # merge the plane-aligned series using the function

				saveobjs=[tag]
				loadnames=[self.getNiftiFile(tagged)]

				# create a detagged version of the tag image
				if makeDetag:
					detag=tag.clone(detagged)
					detagImage(detag,coresize) # turn the tag image into a detagged image
					saveobjs.append(detag)
					loadnames.append(self.getNiftiFile(detagged))

				# load the objects for each plane-aligned image
				if loadPlanes:
					saveobjs+=objs
					loadnames+=[self.getNiftiFile(o.getName()) for o in objs]

				self.saveToNifti(saveobjs)
				for o in saveobjs:
					o.clear()

				f.setObject(self.loadNiftiFiles(loadnames))

		return self.mgr.runTasks(_loadtags(tagobj,makeProspective,loadPlanes,makeDetag,spacing,tryFix),f)

	def createSegObject(self,srcname,segtype):
		f=Future()
		@taskroutine('Generating Segmentation Object')
		def _genseg(srcname,segtype,task):
			with f:
				name=self.getUniqueShortName(srcname,'Seg')
				seg=self.Segment.createSegmentObject(self.getLocalFile(name),name,segtype)
				seg.set(DatafileParams.srcimage,srcname)
				seg.save()
				self.addObject(seg)
				f.setObject(seg)

		return self.mgr.runTasks(_genseg(srcname,segtype),f)

	def createTimeRegStack(self,template,stack,trname=None,loadObject=True):
		'''
		Create a new image series by temporally registering `stack' to `template'. This involves selecting timesteps
		in `stack' which are closest to the timesteps in `template', then copying the images for these timesteps into
		the resulting object. Eg. if `template' has timesteps [0,7] and `stack' has [0,4,6,10], the resulting object
		will have 2 timesteps [0,7] whose images are copied from timesteps 0 and 6 in `stack'. This assumes that
		`template' has fewer timesteps that `stack'.
		'''
		f=Future()
		@taskroutine('Time-registering Images')
		def _timereg(template,stack,trname,loadObject,task):
			with f:
				assert template
				assert stack

				if not trname: # if no name given, choose one based off `stack'
					trname=createShortName('TimeReg',stack.getName(),'to',template.getName())
					if not loadObject: # if we're not reloading the object, ensure the name is unique
						trname=self.getUniqueShortName(trname)

				tempts=template.getTimestepList()
				stackts=stack.getTimestepList()

				assert len(tempts)<=len(stackts),'Template has more timesteps than stack, %r>%r' %(len(tempts),len(stackts))

				obj=stack.plugin.extractTimesteps(stack,trname,None,tempts,True)
				
				assert obj.getTimestepList()==tempts,'%r != %r'%(obj.getTimestepList(),tempts)
				
				if loadObject:
					filenames=self.saveToNifti([obj])
					self._removeNamedObjs(trname)
					obj=self.loadNiftiFiles(filenames)[0]

				f.setObject(obj)

		return self.mgr.runTasks([_timereg(template,stack,trname,loadObject)],f,False)

	def spatialCorrect(self,target,before,after,prefix,extras=[],xyOnly=True,trans=True,logfile=None,cwd=None):
		'''
		Determine the correction for `target'.nii necessary to align the images spatially, then apply this correction
		to `before'.nii to produce `after'.nii, also apply the correction to every i in `extras' which produces and
		`prefix'`i'.nii for each.
		'''
		logfile=logfile or self.getLogFile('spatialcorrect.log')
		cwd=cwd or self.getCWD()

		args=[target+'.nii',before+'.nii',after+'.nii']
		if xyOnly:
			args.append('-xy_only')
		if trans:
			args.append('-translation')
		if extras:
			args+=['-extraimage',str(len(extras)),prefix]+[e+'.nii' for e in extras]

		f1=self.mgr.execBatchProgramTask(self.spatialcorrect,*args,logfile=logfile,cwd=cwd)
		self._checkProgramTask(f1)
		return f1

	def alignShortStack(self,saxname,segname,templatename=None):
		assert os.path.isfile(self.getNiftiFile(saxname)), 'Cannot find %r'%saxname
		origsegname=segname

		# if the given segment is a segmentation object, generate the mask image
		segobj=self.findObject(segname)
		if isinstance(segobj,SegSceneObject):
			saxobj=self.findObject(saxname)
			segname='asaxtemp_SegMask'
			obj=self.Segment.createImageMask(segobj,segname,saxobj,'2 if len(contours)>1 else 3')
			self.saveToNifti([obj])

		# choose names for log files and intermediate/final object names
		cwd=self.getCWD()
		logfile1=self.getLogFile('spatialcorrect1.log')
		logfile2=self.getLogFile('spatialcorrect2.log')
		doffile='shortto3d.dof'

		timeregname='asaxtemp_TimeReg'
		corregname='asaxtemp1_'+timeregname
		corregname2='asaxtemp2_'+timeregname
		tempsaxname='asaxtemp1_'+saxname
		tempsaxname2='asaxtemp2_'+tempsaxname
		tempsegname='asaxtemp1_'+segname
		tempsegname2='asaxtemp2_'+tempsegname
		finalname=self.getUniqueShortName('Aligned',os.path.splitext(saxname)[0])
		finalseg=self.getUniqueShortName('AlignMask',os.path.splitext(origsegname)[0])
		finalsaxnii=self.getNiftiFile(finalname)
		finalsegnii=self.getNiftiFile(finalseg)

		# extract the first timestep of the sax as the frame time-registered to the segmentation
		saxobj=self.findObject(saxname)
		timeregobj=saxobj.plugin.extractTimesteps(saxobj,timeregname,indices=[0])
		self.saveToNifti([timeregobj])

		# correct the time-registered stack using the segmentation and apply to the time-reg, original short axis and segmentation
		f1=self.spatialCorrect(segname,timeregname,corregname,'asaxtemp1_',[saxname,segname],logfile=logfile1,cwd=cwd)
		# correct the time-registered stack again using itself and apply to the time-reg, original short axis and segmentation
		f2=self.spatialCorrect(corregname,corregname,corregname2,'asaxtemp2_',[tempsaxname,tempsegname],logfile=logfile2,cwd=cwd)

		if templatename: # if the template is given, rigidly register the results to it
			# determine the registration of the corrected time-reg to the template image (morpho) and apply to the fixed short-axis
			f3,f4=self.rigidRegisterStack(templatename,corregname2,tempsaxname2,finalname,doffile,self.fixshort,False)
			# apply the dof file from the above to the fixed segmentation
			self.applyHeaderTool(self.getNiftiFile(tempsegname2),finalsegnii,doffile,cwd,False)
		else:
			# move the final results to their new names
			self.mgr.addFuncTask(lambda:shutil.move(self.getNiftiFile(tempsaxname2),finalsaxnii))
			self.mgr.addFuncTask(lambda:shutil.move(self.getNiftiFile(tempsegname2),finalsegnii))
			f3,f4=None,None

		# fix the header values in the final nifti, necessary since IRTK doesn't preserve time info in output niftis
		self.correctNiftiParams(saxname,finalsaxnii)
		# load the nifti files
		self.loadNiftiFiles([finalsaxnii,finalsegnii])
		# delete the temporary files
		self.removeFilesTask(self.getNiftiFile('asaxtemp*'))

		# auto-segment the aligned mask object
		f5=Future()
		@taskroutine('Segmenting Aligned Mask')
		def _segmentMask(task=None):
			with f5:
				mask=self.findObject(finalseg)
				numctrls=16
				if isinstance(segobj,SegSceneObject):
					c=first(segobj.enumContours())
					if c:
						numctrls=len(c[0])

				obj=self.Segment.createSegObjectFromMask('Aligned_'+os.path.splitext(origsegname)[0],mask,numctrls,SegmentTypes._LV)
				obj.filename=self.getLocalFile(obj.filename)
				obj.save()
				self.addObject(obj)
				f5.setObject(obj)

		self.mgr.runTasks(_segmentMask(),f5)

		return f1,f2,f3,f4,f3

	def rigidRegisterStack(self,subjectname,rtargetname,htargetname,finalname,doffile,paramfile,correctNifti):
		'''
		Determine the rigid registration dof file to register image series `rtargetname' to series `subjectname' then
		apply this registration to series `htargetname' to produce series `finalname'. This will create time registered
		versions of `subjectname' and/or `rtargetname' as needed.
		'''
		cwd=self.getCWD()
		logfile1=self.getLogFile('rreg.log')

		regtarget=rtargetname+'_TRtemp'
		regsubject=subjectname+'_TRtemp'

		targettempnii=self.getNiftiFile(regtarget)
		subjecttempnii=self.getNiftiFile(regsubject)
		subjectnii=self.getNiftiFile(subjectname)
		rtargetnii=self.getNiftiFile(rtargetname)

		if htargetname and finalname:
			htargetnii=self.getNiftiFile(htargetname)
			finalnii=self.getNiftiFile(finalname)

		@taskroutine('Time-registering Images')
		def _timeRegister(task):
			target=self.mgr.findObject(rtargetname) or self.Nifti.loadImage(rtargetnii)
			subject=self.mgr.findObject(subjectname) or self.Nifti.loadImage(subjectnii)

			targetts=len(target.getTimestepList())
			subjectts=len(subject.getTimestepList())

			if targetts<subjectts: # if the target has fewer timesteps, time-register the subject to it
				timeregobj=self.createTimeRegStack(target,subject,regsubject,False)
				self.saveToNifti([timeregobj])
				copyfileSafe(rtargetnii,targettempnii)
			elif targetts>subjectts: # conversely time-register the target to the subject
				timeregobj=self.createTimeRegStack(subject,target,regtarget,False)
				self.saveToNifti([timeregobj])
				copyfileSafe(subjectnii,subjecttempnii)
			else: # otherwise just copy both files to their expected filenames
				copyfileSafe(rtargetnii,targettempnii)
				copyfileSafe(subjectnii,subjecttempnii)


		self.mgr.runTasks(_timeRegister())
		f1=self.mgr.execBatchProgramTask(self.rreg,regtarget+'.nii',regsubject+'.nii','-center','-dofout',doffile,'-parin',paramfile,logfile=logfile1,cwd=cwd)
		self._checkProgramTask(f1)

		self.removeFilesTask(self.getNiftiFile('*_TRtemp*'))

		if htargetname and finalname:
			f2=self.applyHeaderTool(htargetnii,finalnii,doffile,cwd)
		else:
			f2=None

		return f1,f2

	def rigidRegisterStackList(self,subjectname,intermedname,targetnames):
		'''
		Rigidly register the images in `targetnames' to the image `subjectname'. If `intermedname' is neither "None"
		nor None, determine what the deformation is to rreg this to `subjectname' and apply that deformation to the
		images in `targetnames'. Otherwise determine the deformation for each image in `targetnames' and apply that
		deformation to the image, ie. rreg each image independently using their own image features.
		'''
		assert os.path.isfile(self.getNiftiFile(subjectname)), 'Cannot find %r'%subjectname
		for tn in targetnames:
			assert os.path.isfile(self.getNiftiFile(tn)), 'Cannot find %r'%tn

		if intermedname=='None':
			intermedname=None

		fresult=[]
		filenames=[]
		doffile=None
		cwd=self.getCWD()

		for tn in targetnames:
			finalname=self.getUniqueShortName('RReg',os.path.splitext(tn)[0],'to',os.path.splitext(subjectname)[0])
			filenames.append(self.getNiftiFile(finalname))

			if doffile==None or intermedname==None:
				# If there's no intermediate then compute the deformation independently for each image.
				# If there is an intermediate, this will calculate its deformation field and apply it to `tn'.
				doffile=tn+'.dof'
				ff=self.rigidRegisterStack(subjectname,intermedname or tn,tn,finalname,doffile,self.fixshort,True)
			else:
				# If there's an intermediate and it's dof has be determined, apply it to `tn'.
				# This line is only reached on the second time through the loop with an intermediate.
				ff=self.applyHeaderTool(tn,finalname,doffile,cwd)

			fresult.append(ff)

		fresult.append(self.loadNiftiFiles(filenames))
		return fresult

	def readIRTKPolydata(self,filename):
		nodes,header=self.VTK.loadPolydataNodes(filename)
		ds=PyDataSet(os.path.basename(filename)+'DS',nodes)
		ds.meta(VTKProps._header,'\n'.join(header))
		return ds

	def createImageGrid(self,obj,w,h,d):
		f=Future()

		@taskroutine('Creating Grid')
		def _createGrid(obj,w,h,d,task):
			with f:
				obj=self.findObject(obj)
				name=self.getUniqueShortName(obj.getName(),'Grid')
				filename=self.getLocalFile(name+'.vtk')
				nodes,inds=generateHexBox(w,h,d)

				ds=PyDataSet(obj.getName()+'DS',nodes,[('inds',ElemType._Hex1NL,inds)])
				ds.getNodes().mul(obj.getVolumeTransform())

				obj= MeshSceneObject(name,ds,self.VTK,filename=filename)
				self.VTK.saveLegacyFile(filename,obj)
				self.addObject(obj)
				f.setObject(obj)

		return self.mgr.runTasks([_createGrid(obj,w,h,d)],f,False)

#	def createIsotropicStack(self,infile,outfile,isoargs=None,shapetype='None',logfile=None,cwd=None):
#		args=[self.resample,infile,outfile,'-isotropic']
#		if isoargs!=None:
#			args.append(str(isoargs))
#
#		shapetype=shapetype.replace(' ','_') # strings from the UI will have _ replaced with spaces so undo this to match names in InterpTypes
#		if shapetype in InterpTypes:
#			args+=InterpTypes[shapetype].split()
#
#		f=self.mgr.execBatchProgramTask(*args,logfile=logfile,cwd=cwd)
#		self._checkProgramTask(f)
#		return f

	def createIsotropicObject(self,obj,cropEmpty):
		f=Future()
		@taskroutine('Creating Isotropic Object')
		def _createIso(obj,isoargs,shapetype,logfile,cwd,task):
			with f:
				obj=self.findObject(obj)

				outname=self.getUniqueShortName(obj.getName(),'Iso')
#				infile=self.getNiftiFile(obj.getName())
				outfile=self.getNiftiFile(outname)
				
				if cropEmpty:
					obj=self.emptyCropObject(obj,False)

#				tempNii=not os.path.isfile(infile)
#
#				if tempNii:
#					self.saveToNifti([obj])
#
#				self.createIsotropicStack(infile,outfile,isoargs,shapetype,logfile,cwd)
#
#				if tempNii:
#					self.removeFilesTask(infile)
				isoobj=obj.plugin.createRespacedObject(obj,obj.getName()+'_Iso')
				resampleImage(obj,isoobj)
				isoobj.plugin.saveObject(isoobj,outfile,setFilenames=True)
				self.addObject(isoobj)

				f.setObject(isoobj)

		return self.mgr.runTasks(_createIso(obj,isoargs,shapetype,logfile,cwd),f)
		
	def setObjectTimestep(self,objname,start,step):
		@taskroutine('Setting Timestep')
		def _setTimestep(objname,start,step,task):
			obj=self.findObject(objname)
			
			obj.setTimestepScheme(start,step)
			
			if isinstance(obj,ImageSceneObject):
				obj.proptuples=[]
				self.saveToNifti([obj])
			
			self.addObject(obj)
		
		self.mgr.runTasks(_setTimestep(objname,start,step))

	def invertTimesteps(self,sourceobj):
		sourceobj=self.findObject(sourceobj)
		assert sourceobj.isTimeDependent
		timesteps=sourceobj.getTimestepIndices()
		images=[]

		for i in range(len(timesteps)):
			ts=timesteps[i][0]
			for ind in timesteps[-i-1][1]:
				image=sourceobj.images[ind].clone()
				image.timestep=ts
				images.append(image)

		nobj=ImageSceneObject(sourceobj.getName()+'_swap',sourceobj.source,images,sourceobj.plugin,True)

		self.saveToNifti([nobj])
		self.addObject(nobj)
		return nobj

	def offsetTimesteps(self,sourceobj,suffix,value,makeProspective=False):
		sourceobj=self.findObject(sourceobj)

		#if not sourceobj.isTimeDependent:
		#	return sourceobj

		if makeProspective:
			timesteps=sourceobj.getTimestepList()
			avgdiff=avgspan(timesteps) #avg(j-i for i,j in zip(timesteps,timesteps[1:]))
			value=avgdiff/2

		for i in sourceobj.images:
			i.timestep+=value

		sourceobj.setName(sourceobj.getName()+suffix)
		sourceobj.source=None

		self.mgr.removeSceneObject(sourceobj)
		self.saveToNifti([sourceobj])
		#self.addObject(sourceobj)

		return self.loadNiftiFiles([self.getNiftiFile(sourceobj.getName())])

	def resampleObject(self,srcname,templatename,isIsotropic):
		f=Future()
		@taskroutine('Resampling Image')
		def _resample(srcname,templatename,isIsotropic,task):
			with f:
				obj=self.findObject(srcname)
				tmplt=self.findObject(templatename)

				name=self.getUniqueShortName(templatename,'Res')
				reobj=tmplt.plugin.extractTimesteps(tmplt,name,timesteps=obj.getTimestepList())
				
				if isIsotropic:
					tslist=reobj.getTimestepList()
					reobj=reobj.plugin.createIntersectObject(name,[reobj,obj],len(tslist),vec3(min(obj.getVoxelSize())))
					reobj.setTimestepList(tslist)
					
				resampleImage(obj,reobj)

				filename=self.saveToNifti([reobj])
				f.setObject(self.loadNiftiFiles(filename))

		return self.mgr.runTasks(_resample(srcname,templatename,isIsotropic),f)

	def extractTimestepsToObject(self,srcname,indices=None,timesteps=None):
		f=Future()
		@taskroutine('Extracting Timesteps')
		def _extract(srcname,indices,timesteps,task):
			with f:
				obj=self.findObject(srcname)

				name=self.getUniqueShortName(obj.getName(),'Extr')
				extrobj=obj.plugin.extractTimesteps(obj,name,indices,timesteps)

				filename=self.saveToNifti([extrobj])
				f.setObject(self.loadNiftiFiles(filename))

		return self.mgr.runTasks(_extract(srcname,indices,timesteps),f)

	def reorderMulticycleImage(self,srcname,starttime,timestep):
		f=Future()
		@taskroutine('Reorder Multicycle Image')
		def _reorder(srcname,starttime,timestep,task):
			with f:
				obj=self.findObject(srcname)
				time1,time2=obj.getTimestepList()[:2]
				images=[]

				for i in obj.images:
					if i.timestep in (time1,time2):
						i=i.clone()
						i.timestep=starttime+(timestep if i.timestep==time1 else 0)
						images.append(i)

				name=self.getUniqueShortName(obj.getName(),'Reord')
				reobj=ImageSceneObject(name,obj.source,images,obj.plugin)

				filename=self.saveToNifti([reobj])
				f.setObject(self.loadNiftiFiles(filename))

		return self.mgr.runTasks(_reorder(srcname,starttime,timestep),f)

	def motionCropObject(self,imgobj,threshold):
#		f=Future()
#		@taskroutine('Motion-cropping Image Object')
#		def _crop(imgobj,threshold,task):
#			with f:
#				imgobj=self.findObject(imgobj)
#				diffimgs=calculateMotionMask(imgobj,task)
#				cobj=applyVolumeMask(imgobj,diffimgs,threshold)
#				f.setObject(self.saveToNifti([cobj]))
#
#		self.mgr.runTasks([_crop(imgobj,threshold)])
#		return self.loadNiftiFiles(f)
		raise NotImplemented,'This cropping method needs work to get correct behaviour still'

	def emptyCropObject(self,imgobj,loadObj=True):
		f=Future()
		@taskroutine('Empty Space-cropping Image Object')
		def _crop(imgobj,loadObj,task):
			with f:
				imgobj=self.findObject(imgobj)

				cropname=self.getUniqueShortName(imgobj.getName(),'Crop')
				cobj=cropObjectEmptySpace(imgobj,cropname,20,False)
				if loadObj:
					f.setObject(self.saveToNifti([cobj]))
				else:
					f.setObject(cobj)

		ff=self.mgr.runTasks(_crop(imgobj,loadObj),f)
		if loadObj:
			return self.loadNiftiFiles(f)
		else:
			return ff

	def refImageCrop(self,imgname,refname,mx,my,mz):
		f=Future()
		@taskroutine('Boundbox-cropping Image Object')
		def _crop(imgname,refname,task):
			with f:
				logfile1=self.getLogFile('region.log')
				cwd=self.getCWD()
				isExtended=mx!=0 or my!=0 or mz!=0

				cropname=self.getUniqueShortName(imgname,'Crop',complen=20)

				imgfile=self.getNiftiFile(imgname)
				reffile=self.getNiftiFile(refname)
				outfile=self.getNiftiFile(cropname)

				if isExtended:
					reffile=self.extendImageStack(refname,mx,my,mz)[1][0]

				ff=self.mgr.execBatchProgramTask(self.region,imgfile,outfile,'-ref',reffile,logfile=logfile1,cwd=cwd)
				self._checkProgramTask(ff)

				if isExtended:
					self.removeFilesTask(reffile)

				self.correctNiftiParams(imgfile,outfile)

				f.setObject(self.loadNiftiFiles([outfile]))

		return self.mgr.runTasks([_crop(imgname,refname)],f)
		
	def extendImageStack(self,stackname,mx=0,my=0,mz=0,value=0):
		obj=self.findObject(stackname)
		ext=extendImage(obj,self.getUniqueShortName(stackname,'Ext'),mx,my,mz,value)
		return ext,self.saveToNifti([ext],True)

	def applyMotionTrack(self,objname,srcname,trackname,isFrameByFrame=False):
		obj=self.findObject(objname)
		srcobj=self.findObject(srcname)
		trackdir=self.getLocalFile(trackname)
		trackfiles=sorted(glob.glob(os.path.join(trackdir,'*.dof.gz')))
		resultname=self.getUniqueShortName(obj.getName(),'Tracked',trackname)
		f=Future()
		
		if not obj or not trackfiles:
			return

		assert isinstance(obj,(ImageSceneObject,MeshSceneObject))
		assert isinstance(obj,(ImageSceneObject,MeshSceneObject))
		assert not srcobj or isinstance(srcobj,(ImageSceneObject,MeshSceneObject))

		if isinstance(obj,MeshSceneObject):
			if srcobj:
				timesteps=srcobj.getTimestepList()
			else:
				timesteps=range(len(trackfiles)+1)

			# single dof file for multiple timesteps rather than on file per step
			if len(trackfiles)==1:
				assert srcobj
				trackfiles=[trackfiles[0]]*(len(timesteps)-1)

			# read the times data so that ptransformation can be set to the right timestep
			if os.path.isfile(os.path.join(trackdir,'times.txt')):
				with open(os.path.join(trackdir,'times.txt')) as o:
					times=map(float,o.readlines())
			else:
				times=[-1]*len(trackfiles)

			assert len(timesteps)==len(trackfiles)+1,'%i != %i'%(len(timesteps),len(trackfiles)+1)

			vecfunc=lambda v:(-v.x(),-v.y(),v.z())
			self.VTK.saveLegacyFile(os.path.join(trackdir,'in.vtk'),obj,datasettype=DatasetTypes._POLYDATA,writeFields=False,vecfunc=vecfunc)

			filelists=[('in.vtk','out%.4i.vtk'%i,dof,times[i]) for i,dof in enumerate(trackfiles)]
			self.mgr.runTasks(applyMotionTrackTask(self.ptransformation,trackdir,False,filelists))

			@taskroutine('Loading Tracked Files')
			def _loadSeq(obj,outfiles,timesteps,name,task):
				with f:
					filenames=[os.path.join(trackdir,o) for o in outfiles]

					objds=obj.datasets[0]

					dds=[objds.clone(objds.getName()+'clone0',True,True,True)]

					indices=list(dds[0].enumIndexSets())
					fields=list(dds[0].enumDataFields())

					for i,ff in enumerate(filenames):
						nodes,_=self.VTK.loadPolydataNodes(ff)
						nodes.mul(vec3(-1,-1,1))
						dds.append(PyDataSet('%sclone%i'%(objds.getName(),i+1),nodes,indices,fields))
						
					# if the dofs are frame-by-frame transformations, rejig the node data to reflect this transformation
					# since the default is assuming each dof is the transformation from frame 0 to frame n
					if isFrameByFrame: 
						n0=dds[0].getNodes()
						for i in range(1,len(dds)):
							n=dds[i].getNodes()
							n.sub(n0)
							n.add(dds[i-1].getNodes())

					result=MeshSceneObject(name,dds,filenames=filenames)
					result.setTimestepList(timesteps)
					
					try:
						obj.plugin.saveObject(result,self.getLocalFile(name),setFilenames=True)
					except ValueError:
						self.VTK.saveObject(result,self.getLocalFile(name),setFilenames=True)
					except NotImplemented:
						self.VTK.saveObject(result,self.getLocalFile(name),setFilenames=True)
						
					self.addObject(result)
					f.setObject(result)

			return self.mgr.runTasks(_loadSeq(obj,[ff[1] for ff in filelists],timesteps,resultname),f)
		else:
			objnii=self.getNiftiFile(obj.getName())
			resultnii=self.getNiftiFile(resultname)

			filelists=[(objnii,'out%.4i.nii'%i,dof,-1) for i,dof in enumerate(trackfiles)]
			self.mgr.runTasks(applyMotionTrackTask(self.transformation,trackdir,True,filelists))

			@taskroutine('Loading Tracked Files')
			def _loadSeq(task):
				with f:
					objs=[self.Nifti.loadObject(os.path.join(trackdir,fl[1])) for fl in filelists]
					result=self.Nifti.createSequence(resultname,objs,srcobj.getTimestepList() if srcobj else None)
					self.Nifti.saveObject(result,resultnii,setFilenames=True)
					self.mgr.addSceneObject(result)
					self.addObject(result)
					f.setObject(result)
					
			return self.mgr.runTasks(_loadSeq(),f)

	def isServerAlive(self,serveraddr=None,serverport=None):
		'''
		Attempts to connect to the server, if this fails the server isn't running or isn't accessible so return False.
		If `serveraddr' or `serverport' are given, these values are used instead of those given by getServerAddrPort().
		'''
		try:
			addr,port=self.getServerAddrPort()

			s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			s.connect((serveraddr or addr,serverport or port)) # throws an exception if the server isn't started
			s.close()
			return True
		except:
			return False

	def sendServerMsg(self,msg,args=(),buffsize=4096,timeout=10.0,serveraddr=None,serverport=None):
		'''Sends a message to a currently running server.'''
		assert msg in ServerMsgs, 'Unknown message %r'%msg
		assert all(a==None or isinstance(a,t) for a,t in zip(args,ServerMsgs[msg][0])), 'Arguments do not have type '+repr(ServerMsgs[msg][0])

		addr,port=self.getServerAddrPort()

		with closing(socket.socket(socket.AF_INET,socket.SOCK_STREAM)) as s: # ensure s.close() is called when the block exits for any reason
			s.settimeout(timeout)
			s.connect((serveraddr or addr,serverport or port)) # connect using addr:port arguments or those given by getServerAddrPort()
			s.sendall(pickle.dumps((msg,args))) # send the pickled message pair
			s.shutdown(socket.SHUT_WR) # let server know we've sent all we're going to send
			received=''
			res=None
			while res==None or len(res)==buffsize: # read the response in `buffsize' chunks
				res=s.recv(buffsize)
				received+=res

			return pickle.loads(received) # return the unpickled response

	def startMotionTrackServer(self):
		'''Starts the server on the local machine if it isn't running and returns the process object, does nothing otherwise.'''

		addr,port=self.getServerAddrPort()
		newport=port
		startserver=False

		# Check to see if there's a server running at addr:port that was started by the current user, if so then use it,
		# otherwise increment port and check again. Once an unused port number if found, use this to start a new server.
		while not startserver:
			try:
				name,msg=self.sendServerMsg(ServerMsgs._Check,serveraddr=addr,serverport=newport) # throws an exception if the server isn't started
				if msg[0]==getUsername(): # if this server is run by the current user, use it
					break
				else:
					newport+=1 # otherwise increment the port number
			except:
				startserver=True # can't connect so start a new server with this port

		if startserver or newport!=port: # save the address and port if it's changed
			self.setServerAddrPort('localhost' if startserver else addr,newport)

		if startserver: # if we can't find a server run by the current user, start one locally
			scriptfile=inspect.getfile(inspect.currentframe())
			logfile=os.path.join(getVizDir(),'motionserver.log')
			args=[sys.executable,'-s',scriptfile,self.serverdir,str(newport),self.motiontrack,self.computetsffd]
			proc=subprocess.Popen(args,stderr = subprocess.STDOUT, stdout=open(logfile,'w'), close_fds=not isWindows)
			time.sleep(5) # wait for the program to launch, especially in OSX which is slow to do anything
			return proc

	def startMotionTrackJob(self,trackname,maskname,dirname,adaptive,chosenparam):
		f=Future()
		@taskroutine('Starting Motion Track Job')
		def _startJob(trackname,maskname,dirname,adaptive,chosenparam,task):
			with f:
				trackobj=self.findObject(trackname)
				numTS=len(trackobj.getTimestepIndices())
				isTagged='tagged' in trackname
				paramfile=self.patient1e6 if isTagged else self.patient1e4

				if chosenparam and os.path.isfile(chosenparam):
					paramfile=chosenparam

				assert trackobj!=None,'Cannot find object '+trackname

				if not isTagged:
					trackfile=self.extendImageStack(trackname,mz=4)[1][0]
					#self._checkProgramTask(f1)
				else:
					trackfile=self.getNiftiFile(trackname)

				if maskname!=None:
					mask=self.findObject(maskname)
					maski=trackobj.plugin.extractTimesteps(trackobj,maskname+'I',timesteps=[0])
					resampleImage(mask,maski)
					maskfile=self.extendImageStack(maski,mz=4)[1][0]
					#self._checkProgramTask(f2)
				else:
					maskfile=None

				if not os.path.exists(paramfile):
					paramfile=self.patient1e6 if isTagged else self.patient1e4
					
				#if dirname:
				#	dirname=self.getUniqueObjName(dirname)

				msg=[True,trackfile,maskfile,paramfile,dirname,adaptive,numTS-1,self.getCWD()]

				self.startMotionTrackServer()

				f.setObject(self.sendServerMsg(ServerMsgs._StartMotionTrack,msg))

		return self.mgr.runTasks(_startJob(trackname,maskname,dirname,adaptive,chosenparam),f,False)

	def startTSFFDJob(self,trackname,maskname,paramfile):
		f=Future()
		@taskroutine('Starting TSFFD Track Job')
		def _startJob(trackname,maskname,paramfile,task):
			with f:
				trackobj=self.mgr.findObject(trackname)
				trackdir=self.getLocalFile(self.getUniqueObjName('tsffdtrack'))
				indices=trackobj.getTimestepIndices()
				paramfile=paramfile or self.tsffd

				os.mkdir(trackdir)

				self.startMotionTrackServer()

				for i,tsinds in enumerate(indices):
					name='image%.4i'%i
					subobj=ImageSceneObject(name,trackobj.source,indexList(tsinds[1],trackobj.images),trackobj.plugin,False)
					self.Nifti.saveImage(os.path.join(trackdir,name+'.nii'),subobj)

				with open(os.path.join(trackdir,'times.txt'),'w') as o:
					for i in range(len(indices)):
						o.write(str(float(i)/len(indices))+'\n')

				f.setObject(self.sendServerMsg(ServerMsgs._StartTSFFD,[trackdir,trackname+'.nii',maskname+'.nii',paramfile]))

		return self.mgr.runTasks(_startJob(trackname,maskname,paramfile),f,False)

	def startGPUNRegMotionTrack(self,imgname,maskname,trackname,paramfile):
		f=Future()
		@taskroutine('Tracking Image With GPU NReg')
		@timing
		def _GPUTrack(imgname,maskname,trackname,paramfile,task):
			with f:
				if not isLinux:
					raise Exception,'GPU NReg is Linux only'
					
				imgobj=self.mgr.findObject(imgname)
				indices=imgobj.getTimestepIndices()

				if not os.path.isfile(paramfile):
					paramfile=self.gpu_nreg_default

				trackname=trackname.strip() or 'GPUNRegTrack_'+imgobj.getName()

				trackname=self.getUniqueObjName(getValidFilename(trackname))
				trackdir=self.getLocalFile(trackname)
				
				if maskname:
					mask=self.findObject(maskname)
					maski=imgobj.plugin.extractTimesteps(imgobj,maskname+'I',timesteps=[0])
					resampleImage(mask,maski)
					maskfile=self.getUniqueLocalFile(makename+'_I')
					self.Nifti.saveObject(maski,maskfile)

				os.mkdir(trackdir)
				names=[]
				results=[]
				
#				# dilate mask
#				if os.path.isfile(maskfile):
#					maskfile=os.path.join(trackdir,'mask.nii')
#					maskobj=self.mgr.findObject(maskname).clone('mask')
#					dilateImageVolume(maskobj,(10,10,10))
#					self.Nifti.saveObject(maskobj,maskfile)

				for i,tsinds in enumerate(indices):
					name='image%.4i'%i
					filename=os.path.join(trackdir,name+'.nii')
					names.append(filename)
					subobj=ImageSceneObject(name,imgobj.source,indexList(tsinds[1],imgobj.images),imgobj.plugin,False)
					self.Nifti.saveObject(subobj,filename)

				task.setMaxProgress(len(names)-1)
				task.setLabel('Tracking Image With GPU NReg')
				
				for i,(img1,img2) in enumerate(successive(names)):
					logfile=os.path.join(trackdir,'%.4i.log'%i)
					args=[img1,img2,'-parin',paramfile,'-dofout','%.4i.dof.gz'%i]
					if os.path.isfile(maskfile):
						args+=['-mask',maskfile]
					r=execBatchProgram(self.gpu_nreg,*args,cwd=trackdir,logfile=logfile)
					results.append(r)
					task.setProgress(i+1)
					
					if r[0]:
						raise IOError,'GPU nreg failed with error code %i (%s)'%r

				f.setObject(results)

		return self.mgr.runTasks(_GPUTrack(imgname,maskname,trackname,paramfile),f,False)

	def checkMotionTrackJobs(self,jids):
		f=Future()
		assert all(isinstance(jid,int) for jid in jids)

		@taskroutine('Checking Jobs')
		def _checkJobs(jids,task):
			with f:
				results=[]
				deadjobs=[]

				for jid in jids:
					name,msg=self.sendServerMsg(ServerMsgs._Stat,(jid,))

					assert name in (ServerMsgs._Except,ServerMsgs._RStat)
					rcode=None

					if name==ServerMsgs._Except:
						self.mgr.showExcept(msg[1],'MotionTrackServer reported an exception when requesting job status.','Exception from Server')
					else:
						rcode,num,total,jobdir=msg
						trackfile='???'
						trackdir=self.getLocalFile(os.path.basename(jobdir))
						inifile=os.path.join(trackdir,'job.ini')
						
						if os.path.isfile(inifile):
							conf=readBasicConfig(inifile)
							trackfile=os.path.split(conf[JobMetaValues._trackfile])[1]

						if rcode==-1 and total==0:
							stat='Unknown Job'
							deadjobs.append(jid)
						elif rcode==0:
							stat='Done, Results in directory motiontrack%i'% jid
						elif rcode==None:
							stat='Running, Progress: %i%%'%int(round(100.0*num/float(total)))
						else:
							stat='Failed, Exit code: %i'%rcode

						stat+=' (Job ID: %i, trackfile: %s)'%(jid,trackfile)
						results.append(stat)

					if rcode==0:
						name,msg=self.sendServerMsg(ServerMsgs._GetResult,(jid,True))
						if name==ServerMsgs._Except:
							self.mgr.showExcept(msg[1],'MotionTrackServer reported an exception when requesting job results.','Exception from Server')

						# TODO: for now do nothing when a job completes correctly since the local files are in the project dir
#						else:
#							os.mkdir(self.project.getProjectFile('motiontrack%s'%str(jid).zfill(3)))
#							for i,ff in enumerate(msg[0]):
#								name=self.getProjectFile('%s/%s.dof.gz'%(str(jid).zfill(3),str(i).zfill(3)))
#								copyfileSafe(ff,name)
#
#							#self.configMap[ConfigNames._jobids].pop(jid)
#							#self.saveConfig()

				f.setObject((results,deadjobs))

		return self.mgr.runTasks(_checkJobs(jids),f,False)


class MotionTrackServer(QtGui.QDialog,Ui_mtServerForm):
	def __init__(self,serverdir,serverport,motiontrackpath,tsffdpath):
		QtGui.QMainWindow.__init__(self)
		self.setupUi(self)
		self.setWindowTitle('%s (Port: %i)'%(self.windowTitle(),serverport))
		self.serverdir=serverdir
		self.jidfile=os.path.join(self.serverdir,'jid.txt')
		self.serverport=serverport
		self.motiontrackpath=motiontrackpath
		self.tsffdpath=tsffdpath
		self.username=getUsername()
		self.runningProcs=[] # list of (Subprocess,jid,directory) triples

		if not os.path.exists(self.serverdir):
			os.mkdir(self.serverdir)

		if not os.path.exists(self.jidfile):
			self.setJID(1)

		class MotionTrackHandler(SocketServer.StreamRequestHandler):
			def handle(hself):
				self.handleRequest(hself.rfile,hself.wfile)

		self.server = SocketServer.TCPServer(('localhost', self.serverport), MotionTrackHandler)
		self.serverThread=threading.Thread(target=self.server.serve_forever)
		self.serverThread.start()

		self.killButton.clicked.connect(self._killJob)

		self.timer=QtCore.QTimer()
		self.timer.timeout.connect(self._updateList)
		self.timer.start(3000)

		self.show()

	def getJID(self):
		with open(self.jidfile) as o:
			return int(o.read().strip())

	def setJID(self,jid):
		with open(self.jidfile,'w') as o: # obviously racy but the probability of 2 simultaneous writes is incredibly low
			o.write(str(jid)+'\n')

	def _updateList(self):
		statlist=[]

		for proc,jid,jobdir in self.runningProcs:
			pid=proc.pid
#			jobdir=os.path.join(jdir,'motiontrack%i'%jid)
			conffile=os.path.join(jobdir,'job.ini')
			conf=readBasicConfig(conffile)

			rcode=conf[JobMetaValues._resultcode]
			numTS=conf[JobMetaValues._numtimesteps]

			numfiles=len(glob.glob(os.path.join(jobdir,'*.dof.gz')))

			rcode=rcode if rcode!=None else proc.poll()

			if rcode!=None and conf[JobMetaValues._resultcode]==None: # update the stored result if necessary
				conf[JobMetaValues._resultcode]=rcode
				storeBasicConfig(conffile,conf)

			stat='Job %i, Status: '%jid
			if rcode==None:
				stat+='Running'
			elif rcode==0:
				stat+='Completed'
			else:
				stat+='Failed, Result: %i'%rcode

			stat+=', PID: %i, Progress: %i%% (%i/%i files)'%(pid,int(round(100.0*numfiles/float(numTS))),numfiles,numTS)

			statlist.append(stat)

		fillList(self.jobList,statlist,self.jobList.currentRow())

	def _killJob(self):
		ind=self.jobList.currentRow()
		if ind>=0:
			msg='This kills the tracking job, are you sure?'
			reply = QtGui.QMessageBox.question(self, 'Kill Job', msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
			if reply == QtGui.QMessageBox.Yes:
				proc=self.runningProcs[ind][0]
				proc.kill()

	def keyPressEvent(self,e):
		if e.key() == QtCore.Qt.Key_Escape:
			self.close()
		else:
			QtGui.QDialog.keyPressEvent(self,e)

	def closeEvent(self,event):
		msg='Closing the server will kill all running jobs, are you sure?'
		reply = QtGui.QMessageBox.question(self, 'Quit', msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

		if reply == QtGui.QMessageBox.Yes:
			self.server.shutdown()

			for proc,jid,jdir in self.runningProcs:
				if proc.returncode==None:
					proc.kill()

			event.accept()
		else:
			event.ignore()

	def handleRequest(self,rfile,wfile):
		try:
			msg,args=pickle.loads(rfile.read())

			if msg==ServerMsgs._Check: # check message, returns the username who started this server
				response=(ServerMsgs._RCheck,(self.username,))

			elif msg==ServerMsgs._StartMotionTrack: # start a motion track job
				jid=self.startMotionTrack(*args)
				response=(ServerMsgs._RStart,(jid,))

			elif msg==ServerMsgs._StartTSFFD:
				jid=self.startComputeTSFFD(*args) # start a TSFFD job
				response=(ServerMsgs._RStart,(jid,))

			elif msg==ServerMsgs._Stat: # get job status
				jid=args[0]
				jobdir=first(h for p,j,h in self.runningProcs if j==jid)
				if jobdir!=None:
					#jobdir=os.path.join(jdir,'motiontrack%i'%jid)
					conf=readBasicConfig(os.path.join(jobdir,'job.ini'))
					numfiles=len(glob.glob(os.path.join(jobdir,'*.dof.gz')))
					response=(ServerMsgs._RStat,(conf[JobMetaValues._resultcode],numfiles,conf[JobMetaValues._numtimesteps],jobdir))
				else:
					response=(ServerMsgs._RStat,(-1,0,0,''))

			elif msg==ServerMsgs._Kill: # kill a given job
				jid=args[0]
				proc=first(p for p,j,h in self.runningProcs if j==jid)
				if proc!=None:
					proc.kill()
				response=(ServerMsgs._RKill,(proc!=None,))

			elif msg==ServerMsgs._GetResult: # get the results for a finished job
				jid,isPaths=args
				jdir=first(h for p,j,h in self.runningProcs if j==jid)
				filelist=glob.glob(os.path.join(jdir,'*.dof.gz'))

				if isPaths: # send the file paths to the results back
					result=list(filelist)
				else: # send the binary data for the files back
					result=[]
					for f in filelist:
						with open(f) as o:
							result.append(o.read())

				response=(ServerMsgs._RGetResult,(result,))
			else:
				raise IOError,'Unhandled message'

		except Exception as e:
			format_exc=str(traceback.format_exc())
			printFlush(format_exc,stream=sys.stderr)
			response=(ServerMsgs._Except,(e,format_exc))

		wfile.write(pickle.dumps(response))

	def startMotionTrack(self,isPaths,trackfile,maskfile,paramfile,dirname,adaptive,numTS,rootdir):
		rootdir=rootdir or self.serverdir

		# calculate the job ID (jid) from the max of the stored jid value and the max numbered motiontrack directory in rootdir
		filejid=self.getJID()
		dirs=glob.glob(os.path.join(rootdir,'motiontrack[0-9]*')) # list the motiontrack dirs in the rootdir (ie. project directory)
		jid=max([0,filejid]+[int(os.path.split(os.path.normpath(d))[1][11:]) for d in dirs])+1

		dirname=dirname or 'motiontrack'
		jobdir=os.path.join(rootdir,'%s_%i'%(dirname,jid))
		
		for i in range(100): # ensure jobdir doesn't exist but don't loop forever
			if not os.path.exists(jobdir):
				break
			jobdir=os.path.join(rootdir,'%s%i_%i'%(dirname,i,jid))
			
		os.makedirs(jobdir)

		self.setJID(jid)

		trackname=trackfile
		maskname=maskfile
		paramname=paramfile

		if not isPaths: # if the file data objects not paths, copy the data into local files
			trackname=os.path.join(jobdir,'track.nii')
			with open(trackname,'w') as o:
				o.write(trackfile)

			if maskfile:
				maskname=os.path.join(jobdir,'mask.nii')
				with open(maskname,'w') as o:
					o.write(maskfile)

			paramname=os.path.join(jobdir,'params.txt')
			with open(paramname,'w') as o:
				o.write(paramfile)

		logfile=os.path.join(jobdir,'output.log')
		args=[self.motiontrackpath,trackname,'-dofout','./','-parin',paramname,'-adaptive',str(adaptive)]

		if maskname:
			args+=['-mask',maskname]

		proc=subprocess.Popen(args,stderr = subprocess.STDOUT, stdout = open(logfile,'w'),cwd=jobdir,close_fds=not isWindows)

		conf={
			JobMetaValues._pid         :int(proc.pid),
			JobMetaValues._resultcode  :None,
			JobMetaValues._numtimesteps:int(numTS),
			JobMetaValues._trackfile   :trackfile,
			JobMetaValues._maskfile    :maskfile,
			JobMetaValues._paramfile   :paramfile,
			JobMetaValues._adaptive    :float(adaptive),
			JobMetaValues._startdate   :time.asctime()
		}

		storeBasicConfig(os.path.join(jobdir,'job.ini'),conf)
		self.runningProcs.append((proc,jid,jobdir))
		return jid

	def startComputeTSFFD(self,jobdir,trackfile,maskfile,paramfile):
		filejid=self.getJID()
		jid=filejid+1

		self.setJID(jid)

		images=sorted(glob.glob(os.path.join(jobdir,'*.nii')))
		logfile=os.path.join(jobdir,'output.log')

		args=[self.tsffdpath,images[0],str(len(images))]+images+['times.txt','-parin',paramfile,'-dofout','out.dof.gz']
		proc=subprocess.Popen(args,stderr = subprocess.STDOUT, stdout = open(logfile,'w'),cwd=jobdir,close_fds=not isWindows)

		conf={
			JobMetaValues._pid         :int(proc.pid),
			JobMetaValues._resultcode  :None,
			JobMetaValues._numtimesteps:1,
			JobMetaValues._trackfile   :trackfile,
			JobMetaValues._paramfile   :paramfile,
			JobMetaValues._maskfile    :maskfile,
			JobMetaValues._startdate   :time.asctime()
		}

		storeBasicConfig(os.path.join(jobdir,'job.ini'),conf)
		self.runningProcs.append((proc,jid,jobdir))
		return jid


if __name__ == '__main__': # run the server program
	printFlush('Starting MotionTrackServer on port',sys.argv[2],'using directory',sys.argv[1])
	app = QtGui.QApplication(sys.argv)
	mt=MotionTrackServer(sys.argv[1],int(sys.argv[2]),sys.argv[3],sys.argv[4])
	sys.exit(app.exec_())