import FreeCAD
import FreeCADGui
import Part
import Draft
from math import pi

def nurbs_flat_cone(face):
    u0,u1,v0,v1 = face.ParameterRange
    angle = 90
    seam = face.Surface.uIso(0)
    p1 = seam.value(v0)
    p2 = seam.value(v1)
    radius1 = face.Surface.Apex.distanceToPoint(p1)
    radius2 = face.Surface.Apex.distanceToPoint(p2)
    t = seam.tangent(v0)[0]
    normal = t.cross(face.Surface.Axis.cross(t))
    c1 = Part.Circle(face.Surface.Apex, normal, radius1)
    c2 = Part.Circle(face.Surface.Apex, normal, radius2)
    ci1 = face.Surface.vIso(v0)
    ci2 = face.Surface.vIso(v1)
    fp1 = c1.parameter(p1)
    fp2 = c2.parameter(p2)
    lp1 = c1.parameterAtDistance(ci1.length(), fp1)
    lp2 = c2.parameterAtDistance(ci2.length(), fp2)
    ce1 = c1.toShape(fp1,lp1)
    ce2 = c2.toShape(fp2,lp2)
    rs = Part.makeRuledSurface(ce1,ce2)
    bs = rs.Surface
    bs.setUKnots([0, 2*pi])
    bs.setVKnots([v0, v1])
    return bs

def nurbs_flat_cylinder(face):
    l1 = face.Surface.uIso(0)
    e1 = l1.toShape(*face.ParameterRange[2:])
    c1 = face.Surface.vIso(face.ParameterRange[2])
    t1 = c1.tangent(c1.FirstParameter)[0]
    l = c1.length()
    e2 = e1.copy()
    e2.translate(t1*l)
    rs = Part.makeRuledSurface(e1,e2)
    bs = rs.Surface
    bs.exchangeUV()
    bs.setUKnots([0, 2*pi])
    return bs

def flatten_face(face):
    tol = 1e-7
    if isinstance(face.Surface, Part.Cylinder):
        flat_face = nurbs_flat_cylinder(face)
    elif isinstance(face.Surface, Part.Cone):
        flat_face = nurbs_flat_cone(face)
    else:
        return None
    u0,u1,v0,v1 = face.Surface.bounds()  

    edges = []
    for e in face.Edges:
        c, fp, lp = face.curveOnSurface(e)
        seam_detected = False
 
        if isinstance(c, Part.Geom2d.Line2d):
            p1 = c.value(fp)
            p2 = c.value(lp)

            if abs(p1.x-u0)+abs(p2.x-u0) < tol:
                #print("seam edge detected1")
                p1.x = u1
                p2.x = u1
                seam_detected = True
                #nl = Part.Geom2d.Line2dSegment(p1,p2)
                #edges.append(nl.toShape(flat_face))
            elif abs(p1.x-u1)+abs(p2.x-u1) < tol:
                #print("seam edge detected2")
                p1.x = u0
                p2.x = u0
                seam_detected = True
                #nl = Part.Geom2d.Line2dSegment(p1,p2)
                #edges.append(nl.toShape(flat_face))
        
                
        if (seam_detected == False) :
           edges.append(c.toShape(flat_face, fp, lp))

    wires = [Part.Wire(el) for el in Part.sortEdges(edges)]
    #f = Part.Face(wires)
    #f.validate()
    #if f.isValid():
        #return f
    #else:
    return Part.Compound(wires)


sel = FreeCADGui.Selection.getSelectionEx()
for so in sel:
    for sub in so.SubObjects:
        if isinstance(sub, Part.Face):
            flat_face = flatten_face(sub)
            if flat_face:
                Part.show(flat_face)
                #sk = Draft.makeSketch(flat_face, autoconstraints=True)
                #sk.Placement.Base = flat_face.Placement.Base
                #FreeCAD.ActiveDocument.recompute()



