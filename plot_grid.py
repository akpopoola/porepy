# -*- coding: utf-8 -*-
"""
Created on Fri Feb 26 19:37:05 2016

@author: keile
"""

import numpy as np
import scipy.sparse as sps
import matplotlib.pyplot as plt
import matplotlib.tri
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection


from core.grids import simplex, structured
from compgeom import sort_points

#------------------------------------------------------------------------------#

def plot_grid(g, info = None, show=True):

#    if isinstance(g, simplex.TriangleGrid):
#        figId, ax = plot_tri_grid(g)
#    elif isinstance(g, structured.TensorGrid) and g.dim == 2:
#        figId, ax = plot_cart_grid_2d(g)
#    elif g.dim == 2:
    if g.dim == 2:
        figId, ax = plot_grid_2d(g)
    else:
        raise NotImplementedError('Under construction')

    if info is not None: add_info( g, info, figId, ax )
    if show: plt.show()

    return figId

#------------------------------------------------------------------------------#

def plot_tri_grid(g):
    """
    Plot triangular mesh using matplotlib.

    The function uses matplotlib's built-in methods for plotting of
    triangular meshes

    Examples:
    >>> x = np.arange(3)
    >>> y = np.arange(2)
    >>> g = simplex.StructuredTriangleGrid(x, y)
    >>> plot_tri_grid(g)

    Parameters
    ----------
    g

    """
    tri = g.cell_node_matrix()
    fig = plt.figure()
    ax = fig.add_subplot(111)
    triang = matplotlib.tri.Triangulation(g.nodes[0], g.nodes[1], tri)
    ax.triplot(triang)
    return fig.number, ax

#------------------------------------------------------------------------------#

def plot_cart_grid_2d(g):
    """
    Plot quadrilateral mesh using matplotlib.

    The function uses matplotlib's bulit-in function pcolormesh

    For the moment, the cells have an ugly blue color.

    Examples:

    >>> g = structured.CartGrid(np.array([3, 4]))
    >>> plot_cart_grid_2d(g)

    Parameters
    ----------
    g grid to be plotted

    """

    # In each direction there is one more node than cell
    node_dims = g.cart_dims + 1

    x = g.nodes[0].reshape(node_dims)
    y = g.nodes[1].reshape(node_dims)

    # pcolormesh needs colors for its cells. Let the value be one
    z = np.ones(x.shape)

    fig = plt.figure()
    #ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    ax = fig.add_subplot(111)
    # It would have been better to have a color map which makes all
    ax.pcolormesh(x, y, z, edgecolors='k', cmap='gray', alpha=0.5)
    return fig.number, ax

#------------------------------------------------------------------------------#

def plot_grid_fractures(g, show=True):
    figId = plot_grid(g, show=False)
    fig = plt.figure( figId )
    face_info = g.face_info
    tags = face_info['tags']
    face_nodes = g.face_nodes.indices.reshape((2, -1), order='F')
    xf = g.nodes
    for ff in np.nditer(np.where(np.isfinite(tags))):
        fn_loc = face_nodes[:, ff]
        plt.plot([xf[0, fn_loc[0]], xf[0, fn_loc[1]]],
                 [xf[1, fn_loc[0]], xf[1, fn_loc[1]]], linewidth=4, color='k')
        # if show:
        #     plt.show()

#------------------------------------------------------------------------------#

def add_info( g, info, figId, ax ):

    def mask_index( p ): return p[0:g.dim]
    def disp( i, p, c, m ): ax.scatter( *p, c=c, marker=m ); ax.text( *p, i )
    def disp_loop( v, c, m ): [ disp( i, ic, c, m ) for i, ic in enumerate( v.T ) ]

    fig = plt.figure( figId )
    info = info.upper()

    if "C" in info: disp_loop( mask_index( g.cell_centers ), 'r', 'o' )
    if "N" in info: disp_loop( mask_index( g.nodes ), 'b', 's' )
    if "F" in info: disp_loop( mask_index( g.face_centers ), 'y', 'd' )

    if "O" in info.upper():
        normals = 0.1*np.array( [ mask_index(n)/np.linalg.norm(n) \
                                  for n in g.face_normals.T ] ).T
        if g.dim == 2:
            [ ax.quiver( *mask_index( g.face_centers[:,f] ), \
                         *normals[:,f], color = 'k', scale=1 )
                                            for f in np.arange( g.num_faces ) ]
        elif g.dim == 3:
            [ ax.quiver( *mask_index( g.face_centers[:,f] ), \
                         *normals[:,f], color = 'k', length=0.25 )
                                            for f in np.arange( g.num_faces ) ]

#------------------------------------------------------------------------------#

def plot_grid_2d( _g ):
    fig = plt.figure()
    ax = fig.add_subplot(111)

    nodes, cells, _  = sps.find( _g.cell_nodes() )
    polygons = []
    for c in np.arange( _g.num_cells ):
        mask = np.where( cells == c )
        cell_nodes = _g.nodes[:, nodes[mask]]
        index = sort_points.sort_point_plane( cell_nodes, _g.cell_centers[:,c] )
        polygons.append( Polygon( cell_nodes[0:2,index].T, True ) )

    p = PatchCollection( polygons, cmap=matplotlib.cm.jet, alpha=0.4 )
    p.set_array( np.zeros( len( polygons ) ) )
    ax.add_collection(p)

    return fig.number, ax

#------------------------------------------------------------------------------#
