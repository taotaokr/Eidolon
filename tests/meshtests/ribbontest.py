# Eidolon Biomedical Framework
# Copyright (C) 2016-7 Eric Kerfoot, King's College London, all rights reserved
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

@mgr.callThreadSafe # immediately calls create() when it's definition is completed
def create():
	nodes=[vec3(0,0,0),vec3(10.0/3,0,0),vec3(20.0/3,0,0),vec3(10,0,0)]
	inds=[(0,2),(2,4)]
	fig=mgr.scene.createFigure("testribbon","Default",FT_RIBBON)
	vb=PyVertexBuffer(nodes)
	ib=PyIndexBuffer(inds)
	fig.fillData(vb,ib,True)
	mgr.controller.setSeeAllBoundBox(BoundBox(nodes))
	mgr.repaint()
	return fig # returned value gets assigned to the name `create', this prevents it being cleaned up when create() exits
