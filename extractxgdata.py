#
#   extractxgdata.py - Simple XG data extraction tool
#   Copyright (C) 2013,2014  Michael Petch <mpetch@gnubg.org>
#                                          <mpetch@capp-sysware.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Lesser General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Lesser General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

from __future__ import with_statement
import sys
import struct
import uuid
import os
import argparse
import xgimport
import xgzarc
import xgstruct
import pprint

def parseoptsegments(parser, segments):

    segmentlist = segments.split(',')
    for segment in segmentlist:
        if segment not in ['all', 'comments', 'gdhdr', 'thumb', 'gameinfo',
                           'gamefile', 'rollouts', 'idx']:
            parser.error("%s is not a recognized segment" % segment)
    return segmentlist


def directoryisvalid(parser, dir):

    if not os.path.isdir(dir):
        parser.error("directory path '%s' doesn't exist" % dir)
    return dir


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='XG data extraction utility',
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-d", metavar='DIR', dest="outdir",
                        help="Directory to write segments to "
                        "(Default is same directory as the import file)\n",
                        type=lambda dir:
                        directoryisvalid(parser, dir), default=None)
    parser.add_argument('files', metavar='FILE', type=str, nargs='+',
                        help='An XG file to import')
    args = parser.parse_args()

    for xgfilename in args.files:
        xgbasepath = os.path.dirname(xgfilename)
        xgbasefile = os.path.basename(xgfilename)
        xgext = os.path.splitext(xgfilename)
        if (args.outdir is not None):
            xgbasepath = args.outdir

        try:
            xgobj = xgimport.Import(xgfilename)
            print ('Processing file: %s' % xgfilename)
            fileversion = -1
            # To do: move this code to XGImport where it belongs
            for segment in xgobj.getfilesegment():
                segment.copyto(os.path.abspath(
                        os.path.join(xgbasepath,
                        xgbasefile[:-len(xgext[1])] + segment.ext)))

                if segment.type == xgimport.Import.Segment.XG_GAMEFILE:
                    segment.fd.seek(os.SEEK_SET, 0)
                    while True:
                        rec = xgstruct.GameFileRecord(
                                version=fileversion).fromstream(segment.fd)
                        if rec is None:
                            break
                        if isinstance(rec, xgstruct.HeaderMatchEntry):
                            fileversion = rec.Version
                        elif isinstance(rec, xgstruct.UnimplementedEntry):
                            continue
                        pprint.pprint (rec,width=160)
                elif segment.type == xgimport.Import.Segment.XG_ROLLOUTS:
                    segment.fd.seek(os.SEEK_SET, 0)
                    while True:
                        rec = xgstruct.RolloutFileRecord().fromstream(segment.fd)
                        if rec is None:
                            break
                        pprint.pprint (rec,width=160)

        except (xgimport.Error, xgzarc.Error) as e:
            print (e.value)
