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
from __future__ import division

import h5py
import plots
import numpy as np
import matplotlib
import matplotlib.pyplot as plt



def _ff(n):
    """Formats frame names """
    return "frame%(#)06d"%{"#":n}

def _fd(str_,n):
    """ formats dset names"""
    return str_ + "_%(#)07d"%{"#":n}
def extract_track(F,frame_num,part_num,track_group,iden_group,trk):
    """starting with particle part_num in frame_num extracts the path
    going forwards"""
    trk.append((F[_ff(frame_num)][_fd('x',iden_group)][part_num],
                F[_ff(frame_num)][_fd('y',iden_group)][part_num]))
    
    nxt = F[_ff(frame_num)][_fd('next_part',track_group)][part_num]
    
    if  nxt != -1:
        extract_track(F,frame_num+1,nxt,track_group,iden_group,trk)
    return trk
        
def print_info(F,frame_num,part_num,comp_num):
    """Prints returns (prev_part,next_part,track_id) for the given
    particle and computation"""
    return (F[_ff(frame_num)][_fd('prev_part',comp_num)][part_num],
            F[_ff(frame_num)][_fd('next_part',comp_num)][part_num],
            F[_ff(frame_num)][_fd('track_id',comp_num)][part_num])


def plot_tracks(track_comp_key,region,init_frame,conn):
    """Takes in a track_comp key and a region of the image and plots
    the tracks going forward of all the particles that are in the
    initial frame

    region = [x_offset y_offset x_len y_len]
    """

    # make sure track id is valid
    # extract comp_id
    (fin,dset_key) = conn.execute("select fout,dset_key from comps where\
    function='tracking' and comp_key=?",
                                  (track_comp_key,)).fetchone()
    (d_temp,) = conn.execute("select temp from dsets where key = ?",
                             (dset_key,)).fetchone()
    (iden_key, ) = conn.execute("select iden_key from tracking_prams where comp_key=?",
                                (track_comp_key,)).fetchone()

    # open file
    F = h5py.File(fin,'r')

    try:
        
        # extract list of particles in ROI
        x = F[_ff(init_frame)][_fd('x',iden_key)][:]
        y = F[_ff(init_frame)][_fd('y',iden_key)][:]

        ind = matplotlib.mlab.find((x>region[0]) * (y>region[1]) \
              * (x<(region[0] + region[2] ) )*( y<(region[1] + region[3])))

        
        
        
        # loop over particles in region and extract tracks
        tracks = [extract_track(F,init_frame,j,track_comp_key,iden_key,[]) for j in ind]
        # set up figure
        (fig,ax) = plots.set_up_plot()

        ax.set_title(str(d_temp))

        def trk_len_hash(trk):
            return len(trk)
        def trk_disp_hash(trk):
            return np.sqrt((np.sum(np.array(trk[-1]) - np.array(trk[0]))**2))

        trk_hash = trk_disp_hash
        
        t_len = [trk_hash(trk) for trk in tracks]
        cm = plots.color_mapper(min(t_len),max(t_len))
        # loop over tracks and plot
        [ax.plot([t[0] for t in trk],[t[1] for t in trk],'-',
                 color=cm.get_color(trk_hash(trk)))
         for trk in tracks]

        # plot the starting points
        ax.plot(x[ind],y[ind],'xk')
        
        ax.set_aspect('equal')
        plt.draw()
        
    finally:
        # close hdf file and clean up
        F.close()
        del F
