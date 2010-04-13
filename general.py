#Copyright 2010 Thomas A Caswell
#tcaswell@uchicago.edu
#http://jfi.uchicago.edu/~tcaswell
#
#This program is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; either version 3 of the License, or (at
#your option) any later version.
#
#This program is distributed in the hope that it will be useful, but
#WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program; if not, see <http://www.gnu.org/licenses>.

import sqlite3
import h5py
import lib.pov 
import lib.plots 
import lib.util 


def open_conn():
    '''Opens the data base at the standard location and returns the connection'''
    conn =sqlite3.connect('/home/tcaswell/colloids/processed/processed_data.db')
    conn.execute('PRAGMA foreign_keys = ON;')
    return conn

def get_fout_comp(key,conn,func):
    '''Returns the fout name and the computation number for the iden on the dataset given by key'''
    res = conn.execute("select fout,comp_key from comps where dset_key == ? and function == ?",
                       (key,func)).fetchall()
    if not len(res) == 1:
        raise lib.util.dbase_error("either no or too many iden operations found")

    return res[0]
    # 

def get_xyzI_f(h5file,frame,comp_num):
    '''Extracts the x,y,z,I from the given frame and comp_num from the open file handed in '''

    cords = lib.util.Cords3D()
    cords.x = h5file["/frame%(#)06d"%{"#":frame}+"/x_%(#)07d"%{"#":comp_num}][:]
    cords.y = h5file["/frame%(#)06d"%{"#":frame}+"/y_%(#)07d"%{"#":comp_num}][:]
    cords.z = h5file["/frame%(#)06d"%{"#":frame}+"/z_%(#)07d"%{"#":comp_num}][:]
    cords.I = h5file["/frame%(#)06d"%{"#":frame}+"/intensity_%(#)07d"%{"#":comp_num}][:]

    return cords


def get_xyzI(key,conn,frame):
    '''Returns four vectors for x,y,z,I for the data set given by key'''

    (fname, comp_number) = get_fout_comp(key,conn,'link3D')

    f = h5py.File(fname,'r')

    cord = get_xyzI_f(f,frame,comp_number)
    f.close()
    
    return cord

    pass


def make_gofr_2Dv3D(conn):
    keys = conn.execute("select key from dsets where dtype = 'z'").fetchall()
    for k in keys:
        plots.make_2dv3d_plot(k[0],conn,'figures/2Dv3D/%(#)02d.png'%{"#":k[0]})
        

def make_z_slices_series(conn,key,step,base_dir,base_name):
    """Takes in a data base connection, a dset key, a directory to dump to, and a basename """

    # check to make sure base_dir exists
    cords = get_xyzI(key,conn,0)

    lib.pov.make_z_slices(cords,step,base_dir+'/'+base_name)
    pass

