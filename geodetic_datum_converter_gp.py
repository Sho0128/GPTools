#coding:utf-8

"""
tokyo -> jgd2000
linear method
"""


import os
import arcpy


def main():
    # input feature class or shape file
    inputfc = arcpy.GetParameterAsText(0)
    # output feature class
    outputfc = arcpy.GetParameterAsText(1)

    gdc = GeodeticDatumConverter(inputfc, outputfc)

    arcpy.AddMessage("Geometry type: " + gdc.geomtype)

    if gdc.geomtype == "Point":
        gdc.insert_geometry_point()
    elif gdc.geomtype == "Polyline":
        gdc.insert_geometry_polyline()
    elif gdc.geomtype == "Polygon":
        gdc.insert_geometry_polygon()
    else:
        arcpy.AddMessage("Geometry type error.")

class GeodeticDatumConverter(object):
    def __init__(self, inputfc, outputfc):
        arcpy.SetLogHistory(False)
        arcpy.env.overwriteOutput = True
        self.inputfc = inputfc
        self.inputtype = arcpy.Describe(inputfc).dataType
        self.geomtype = arcpy.Describe(inputfc).shapeType
        self.outputfc = outputfc
        self.sr = arcpy.SpatialReference(4612)
        arcpy.CreateFeatureclass_management(os.path.dirname(self.outputfc), os.path.basename(self.outputfc),
                                            self.geomtype, self.inputfc, spatial_reference=self.sr)

    def insert_geometry_point(self):
        trgfldlist = self.__get_field_list()
        srchcur = arcpy.da.SearchCursor(self.inputfc, trgfldlist)
        insrcur = arcpy.da.InsertCursor(self.outputfc, trgfldlist)
        for row in srchcur:
            rowlist = list(row)
            newpt = self.__mk_geom_array(rowlist)
            rowlist[0] = arcpy.PointGeometry(newpt, self.sr)
            insrcur.insertRow(tuple(rowlist))
        del srchcur
        del insrcur

    def insert_geometry_polyline(self):
        trgfldlist = self.__get_field_list()
        srchcur = arcpy.da.SearchCursor(self.inputfc, trgfldlist)
        insrcur = arcpy.da.InsertCursor(self.outputfc, trgfldlist)
        for row in srchcur:
            rowlist = list(row)
            array = self.__mk_geom_array(rowlist)
            rowlist[0] = arcpy.Polyline(array, self.sr)
            insrcur.insertRow(tuple(rowlist))
        del srchcur
        del insrcur

    def insert_geometry_polygon(self):
        trgfldlist = self.__get_field_list()
        srchcur = arcpy.da.SearchCursor(self.inputfc, trgfldlist)
        insrcur = arcpy.da.InsertCursor(self.outputfc, trgfldlist)
        for row in srchcur:
            rowlist = list(row)
            array = self.__mk_geom_array(rowlist)
            rowlist[0] = arcpy.Polygon(array, self.sr)
            insrcur.insertRow(tuple(rowlist))
        del srchcur
        del insrcur

    def __mk_geom_array(self, rowlist):
        array = arcpy.Array()
        try:
            for part in rowlist[0]:
                part_array = arcpy.Array()
                for pnt in part:
                    newpt = arcpy.Point()
                    newpt.X, newpt.Y = self.__linear_method(pnt.X, pnt.Y)
                    part_array.add(newpt)
                array.add(part_array)
            return array
        except TypeError:
            newpt = arcpy.Point()
            newpt.X, newpt.Y = self.__linear_method(rowlist[0].centroid.X, rowlist[0].centroid.Y)
            return newpt

    def __linear_method(self, tokyoX, tokyoY):
        jgdX = tokyoX - 0.000046038*tokyoY - 0.000083043*tokyoX + 0.010040
        jgdY = tokyoY - 0.00010695*tokyoY + 0.000017464*tokyoX + 0.0046017
        return jgdX, jgdY

    def __get_field_list(self):
        fieldlist = arcpy.ListFields(self.outputfc)        
        trgfldlist = ["Shape@"]
        trgfldlist += [f.name for f in fieldlist if f.name not in ["OBJECTID","Shape","Shape_Length","Shape_Area"]]
        return trgfldlist        

if __name__ == "__main__":
    main()