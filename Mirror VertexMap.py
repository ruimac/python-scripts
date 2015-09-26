# Script by RuiMac - 09-2015

import c4d
import sys
from c4d import gui

# IDs of the dialog elements
OPTION=1000
TH_TEXT=1009
THRESHOLD=1010
WHAT=1020
BLEND=1030
NEWTAG=1040
GROUP_OPTIONS = 2000
BTN_OK = 2001
BTN_CANCEL = 2002

# dialog definition
class OptionsDialog(gui.GeDialog):
  def CreateLayout(self):
    self.SetTitle('Select Mirror Axis')
    
    self.AddRadioGroup(OPTION,c4d.BFH_SCALEFIT,columns=2,rows=3)
    self.AddChild(OPTION,0,"+X to -X      ")
    self.AddChild(OPTION,1,"-X to +X")
    self.AddChild(OPTION,2,"+Y to -Y      ")
    self.AddChild(OPTION,3,"-Y to +Y")
    self.AddChild(OPTION,4,"+Z to -Z      ")
    self.AddChild(OPTION,5,"-Z to +Z")
    
    self.SetInt32(OPTION,0)
    
    self.AddSeparatorH(200)
    
    self.AddRadioGroup(WHAT,c4d.BFH_SCALEFIT,columns=3,rows=0)
    self.AddChild(WHAT,0,"Replace  ")
    self.AddChild(WHAT,1,"Add  ")
    self.AddChild(WHAT,2,"Blend")
    
    self.SetInt32(WHAT,0)
    
    self.AddEditSlider(BLEND,c4d.BFH_FIT)
    self.SetFloat(BLEND,.5,min=0.0,max=1.0,step=.01,format=c4d.FORMAT_PERCENT)
    self.Enable(BLEND,False)
    
    self.AddSeparatorH(200)
    
    self.AddStaticText(TH_TEXT,c4d.BFH_LEFT,name="Threshold")
    self.AddEditSlider(THRESHOLD,c4d.BFH_FIT)
    
    self.SetFloat(THRESHOLD,0.01,min=0.0,max=100.0,step=.01,format=c4d.FORMAT_METER)
    
    self.AddSeparatorH(200)
    
    self.AddCheckbox(NEWTAG,c4d.BFH_LEFT,initw=0,inith=10,name="Create new VertexMap Tag")
    
    self.AddSeparatorH(200)
    
    # Buttons - an Ok and Cancel button:
    self.GroupBegin(GROUP_OPTIONS, c4d.BFH_CENTER, 2, 1)
    self.AddButton(BTN_OK, c4d.BFH_SCALE, name='OK')
    self.AddButton(BTN_CANCEL, c4d.BFH_SCALE, name='Cancel')
    self.GroupEnd()
    self.ok = False
    return True

  # React to user's input:
  def Command(self, id, msg):
    # enable the Blend slider only if the mode is set to Blend
    self.Enable(BLEND,self.GetInt32(WHAT)==2)
    
    if id==BTN_CANCEL:
      self.Close()
    elif id==BTN_OK:
      self.ok = True
      self.option = self.GetInt32(OPTION)
      self.threshold = self.GetFloat(THRESHOLD)
      self.what = self.GetInt32(WHAT)
      self.blend = self.GetFloat(BLEND)
      self.newtag = self.GetBool(NEWTAG)
      self.Close()
    return True

# --------------------------------------------------------------

def get_nearest(pt,pt_list,threshold,mode):
    
    # the list is empty, return
    if len(pt_list)==0: return -1
    
    smallest=sys.float_info.max # starts with the largest float number
    index=-1 # no index yet
    
    # cases 0 and 1 are reduced to 0
    # cases 2 and 3 are reduced to 1
    # cases 4 and 5 are reduced to 2
    mode=int(mode/2)
    
    # nothing to delete... yet
    to_delete=-1

    for to_del,atom in enumerate(pt_list):
        
        cd=atom[0] # the coordinates inside the list
        i=atom[1] # the index inside the list
        
        if mode==0: # +X to -X or -X to +X
            difference=c4d.Vector(abs(cd.x),cd.y,cd.z)-c4d.Vector(abs(pt.x),pt.y,pt.z)
            length=difference.GetLength()
            if length<threshold: # only if smaller than threshold
                if length<smallest: # only if smaller than previous value
                    smallest=length
                    index=i
                    to_delete=to_del
                    

        if mode==1 : # +Y to -Y or -Y to +Y
            difference=c4d.Vector(cd.x,abs(cd.y),cd.z)-c4d.Vector(pt.x,abs(pt.y),pt.z)
            length=difference.GetLength()
            if length<threshold: # only if smaller than threshold
                if length<smallest: # only if smaller than previous value
                    smallest=length
                    index=i
                    to_delete=to_del
                        
        if mode==2: # +Z to -Z or -Z to +Z
            difference=c4d.Vector(cd.x,cd.y,abs(cd.z))-c4d.Vector(pt.x,pt.y,abs(pt.z))
            length=difference.GetLength()
            if length<threshold: # only if smaller than threshold
                if length<smallest: # only if smaller than previous value
                    smallest=length
                    index=i
                    to_delete=to_del

    return index,to_delete
                

def main():
    
    tags=doc.GetActiveTags() # get all the active tags
    
    the_tag=None
    
    for vertex_tag in tags:
        # if the tag is a VertexMap tag...
        if vertex_tag.GetType()==5682: the_tag=vertex_tag # get the last one

    # none was found?
    if the_tag==None: return
    
    # get the object that contains the tag
    the_object=the_tag.GetObject()
    
    # if it is not a polygonal object
    if the_object.GetType()!=5100: return
    
    # get a list with all the VertexMap values
    values=the_tag.GetAllHighlevelData()
    
    # show the dialog
    dlg=OptionsDialog()
    dlg.Open(c4d.DLG_TYPE_MODAL, defaultw=200, defaulth=50)
    
    # the user pressed Cancel
    if not dlg.ok:
        return
    
    # get the parameters
    the_option = dlg.option
    the_threshold = dlg.threshold
    the_what = dlg.what
    the_blend = dlg.blend
    create_new = dlg.newtag
    
    # get a list with all the points coordinates of the object
    all_points=the_object.GetAllPoints()
    
    # transform a list of coordinates into a list of coordinates plus index
    # Vector(x,y.z) -> [Vector(x,y,z),i]
    all_points=map(lambda (i,x): [x,i],enumerate(all_points))
    # copy the list
    new_list=list(all_points)
    
    # create new lists with just the relevant points, according to the mirroring plane
    if the_option==0:
        new_list=filter(lambda x: x[0].x<=0,new_list) # keep just the coordinates with x<=0
        all_points=filter(lambda a: a[0].x>=0, all_points) # keep just the coordinates with x>=0

    if the_option==1:
        new_list=filter(lambda x: x[0].x>=0,new_list) # keep just the coordinates with x>=0
        all_points=filter(lambda a: a[0].x<=0, all_points) # keep just the coordinates with x<=0

    if the_option==2:
        new_list=filter(lambda x: x[0].y<=0,new_list) # keep just the coordinates with y<=0
        all_points=filter(lambda a: a[0].y>=0, all_points) # keep just the coordinates with y>=0

    if the_option==3:
        new_list=filter(lambda x: x[0].y>=0,new_list) # keep just the coordinates with y>=0
        all_points=filter(lambda a: a[0].y<=0, all_points) # keep just the coordinates with y<=0

    if the_option==4:
        new_list=filter(lambda x: x[0].z<=0,new_list) # keep just the coordinates with z<=0
        all_points=filter(lambda a: a[0].z>=0, all_points) # keep just the coordinates with z>=0

    if the_option==5:
        new_list=filter(lambda x: x[0].z>=0,new_list) # keep just the coordinates with z>=0
        all_points=filter(lambda a: a[0].z<=0, all_points) # keep just the coordinates with z<=0
    
    # announce the mirroring operation in the status bar
    c4d.StatusSetText("Mirroring VertexMap")
    
    # for speeding purposes
    bar=0.0
    bar_step=100.0/(len(all_points))
    
    # go through all the points
    for atom in all_points:
        
        pt=atom[0] # the coordinates inside the list
        i=atom[1] # the index inside the list
        
        # update the status bar
        c4d.StatusSetBar(int(bar))
        bar+=bar_step
        
        if len(new_list)>0:
            # find the nearest symmetrical point
            nearest,to_delete=get_nearest(pt,new_list,the_threshold,the_option)
            # if one was found, depending on the threshold...
            if nearest!=-1:
                if the_what==0: # Replace
                    values[nearest]=values[i]
                elif the_what==1: # Add
                    values[nearest]=min(values[nearest]+values[i],1.0)
                else: # Blend
                    values[nearest]=c4d.utils.MixNum(values[nearest],values[i],the_blend)
                
                # if there is something to delete from the list...
                if to_delete!=-1: new_list.pop(to_delete)
                # this will speed up searches because once a good candidate is found, it should not be used again
     
    # clear the status bar
    c4d.StatusClear()

    if create_new is False:
        # store the previous state of the tag so that the change can be undone
        doc.StartUndo()
        doc.AddUndo(c4d.UNDOTYPE_CHANGE,the_tag)
    
        # store the updated list
        the_tag.SetAllHighlevelData(values)
        doc.EndUndo()
    else:
        # store the previous state of the tag so that the change can be undone
        doc.StartUndo()
        vertexmaptag=the_tag.GetClone()
        the_object.InsertTag(vertexmaptag,the_tag)
        doc.AddUndo(c4d.UNDOTYPE_NEW,vertexmaptag)
        # store the updated list
        vertexmaptag.SetAllHighlevelData(values)
        doc.EndUndo()
       
    
    # refresh the scene
    c4d.EventAdd()
    
if __name__=='__main__':
    main()