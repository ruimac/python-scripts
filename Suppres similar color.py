# Script by RuiMac - 09-2015

import c4d
from c4d import gui
#Welcome to the world of Python

def replace(obj,m1,m2):
    # while there are still objects...
    while obj:
        # get all the tags of the object
        tags=obj.GetTags()
        # if there are any tags in the objec
        if tags!=[]:
            # go through all the tags
            for tag in tags:
                # if the tag is a Texture tag...
                if tag.GetType()==c4d.Ttexture:
                    # if the material is material2
                    if tag[c4d.TEXTURETAG_MATERIAL]==m2:
                        # report a change to the undo stack so that it can be undone
                        doc.AddUndo(c4d.UNDOTYPE_CHANGE,tag)
                        # change the Texture tag material to material1
                        tag[c4d.TEXTURETAG_MATERIAL]=m1
            # update the document
            obj.Message(c4d.MSG_UPDATE)
        # recursively call itself pointing to the child object, if any
        replace(obj.GetDown(),m1,m2)
        # no more childs... advance to the next object, if any
        obj=obj.GetNext()
    return None

def main():
    # get all materials
    materials=doc.GetActiveMaterials()
    # if there are no materials, return
    if materials==[]: return
    
    # ask the user how different can the colors be
    diff=gui.InputDialog("How different (%) can the color be?","")
    # if the user gave no value, return
    if diff=="": return
    
    # delete the "%", if any is found
    diff=diff.replace("%","")
    
    # try to evaluate the value
    try:
        diff=eval(diff)
    # there was an error. Probably not a numeric value
    except (NameError,SyntaxError):
        gui.MessageDialog("That is not an acceptable value.")
        return
    
    # change from 0->100 to 0->1
    diff=diff/100.0
    
    # initialize variables
    pointer1=0
    repl=0
    whole=len(materials)
    
    # prepare to undo all changes
    doc.StartUndo()
    c4d.StatusSetText("Scanning through materials")
    
    # while there are still materials to process
    while pointer1<len(materials):
        count=len(materials)
        # update the status bar
        c4d.StatusSetBar(100-100*(count-pointer1)/count)
        
        # get a material
        m1=materials[pointer1]
        # point to the next one
        pointer2=pointer1+1
        # go through all the remaining materials
        while pointer2<len(materials):
            # get a material
            m2=materials[pointer2]
            # get the colors of both materials
            color1=m1[c4d.MATERIAL_COLOR_COLOR]
            color2=m2[c4d.MATERIAL_COLOR_COLOR]
            # calculate the difference between the colors of both materials
            r=abs(color2.x-color1.x)
            g=abs(color2.y-color1.y)
            b=abs(color2.z-color1.z)

            # if the difference all color components is smaller or equal to the allowed change, delete the material
            if r<=diff and g<=diff and b<=diff:
                # report in the Console what materials is being deleted
                print "Material "+m2.GetName()+" is very similar do material "+m1.GetName()+". Replacing!"
                # increase the deleted count
                repl+=1
                # replace the ocurrences of material2 by material1, starting with the in the first object in the document
                replace(doc.GetFirstObject(),m1,m2)
                # remove the material2 from the list
                materials.pop(pointer2)
                # store the deletion in the Undo list so it can be undone
                doc.AddUndo(c4d.UNDOTYPE_DELETE,m2)
                # delete material2 from the document
                m2.Remove()
            # advance to the next material
            pointer2=pointer2+1
        
        # advance to the next material
        pointer1=pointer1+1
    
    # clear the status bat
    c4d.StatusClear()
    
    # update the document
    c4d.EventAdd(0)
    # finish the undo recording
    doc.EndUndo()
    
    # if there were any deletions/replacements, report their number in a pop-up dialog
    if repl!=0:
        gui.MessageDialog(str(repl)+" materials were replaced. From a total of "+str(whole)+", now there are only "+str(whole-repl))
        
if __name__=='__main__':
    main()
