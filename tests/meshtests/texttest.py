# Eidolon Biomedical Framework
# Copyright (C) 2016-8 Eric Kerfoot, King's College London, all rights reserved
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

import sys
sys.path.append(scriptdir+'..')

from eidolon import FT_TEXT, H_LEFT, V_CENTER, MeshSceneObject, ReprType, rotator, vec3, halfpi
from TestUtils import generateArrowDS

ds=generateArrowDS(12) # create arrow, resize and move away from origin
nodes=ds.getNodes()
nodes.mul(5)
nodes.mul(rotator(vec3.Y(),halfpi))
nodes.add(vec3(1,2,3))

obj=MeshSceneObject('Arrow',ds)
mgr.addSceneObject(obj)

rep=obj.createRepr(ReprType._volume)
mgr.addSceneObjectRepr(rep)


@mgr.callThreadSafe
def fig():
    tfig=mgr.scene.createFigure('text','Default',FT_TEXT)
    tfig.setText('If you can read this,\nthe test passes')
    tfig.setHAlign(H_LEFT)
    tfig.setVAlign(V_CENTER)
    tfig.setOverlay(False)
    tfig.setCameraAlign(True)
    tfig.setVisible(True)
    tfig.setPosition(ds.getNodes()[-1])
    return tfig # need to return tfig so that it's stored as the variable fig, otherwise it will get collected


mgr.setCameraSeeAll()
mgr.controller.setZoom(15)
mgr.repaint()
