import bpy
import sys
import math
import mathutils
from mathutils import Euler
from mathutils import Matrix

class cs418Import():
    
    def __init__(self):
        self.state_color = (1,1,1)
        self.material_count = 0
        self.pngname = "bogus.png"
        
        color_name = f'color{self.material_count}'
        self.material_count = self.material_count + 1
        mat = bpy.data.materials.new(color_name)
        mat.use_nodes = True
        tree = mat.node_tree
        nodes = tree.nodes
        bsdf = nodes["Principled BSDF"]
        bsdf.inputs["Base Color"].default_value = (1, 1, 1, 1)
        mat.diffuse_color = (1, 1, 1, 1)
        self.current_material = mat   
        bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (0,0,0,0)  
        bpy.data.worlds["World"].cycles.max_bounces=3
        bpy.data.scenes["Scene"].frame_end=1
        bpy.data.scenes["Scene"].render.image_settings.compression=0

    def clearScene(self):
        scn = bpy.context.scene
        scn.render.engine = 'CYCLES'
        scn.world.use_nodes = True
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()
        

    def rgbfunc(self,args):
        rcolor = float(args.pop(0))
        gcolor = float(args.pop(0))
        bcolor = float(args.pop(0))
        color_name = f'color{self.material_count}'
        self.material_count = self.material_count + 1
        mat = bpy.data.materials.new(color_name)
        mat.use_nodes = True
        tree = mat.node_tree
        nodes = tree.nodes
        bsdf = nodes["Principled BSDF"]
        bsdf.inputs["Base Color"].default_value = (rcolor, gcolor, bcolor, 1)
        mat.diffuse_color = (rcolor, gcolor, bcolor, 1)
        self.current_material = mat 
        self.state_color = (rcolor,gcolor,bcolor)

    def spherefunc(self,args):
        '''
        Adds a sphere to the list of objects to be rendered
        '''
        x = float(args.pop(0))
        y = float(args.pop(0))
        z = float(args.pop(0))
        r = float(args.pop(0))
        #sph = bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=10, radius = 0.05, location=(0.2, -0.2 ,-0.5))
        sph = bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3,radius = r, location=(x, y , z))
        sph_obj = bpy.context.object
        bpy.ops.object.shade_smooth()
        sph_obj.active_material = self.current_material

    def vecs_to_euler(self,x,y,z):
        rot_order = (0,1,2)
        # Change the order rotation is applied.
        MATRIX_IDENTITY_3x3 = Matrix([[1,0,0],[0,1,0],[0,0,1]])
        MATRIX_IDENTITY_4x4 = Matrix([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])

        # Clamp all values between 0 and 360, values outside this raise an error.
        mats=[mathutils.Matrix.Rotation(x%360,3,'X'),
              mathutils.Matrix.Rotation(y%360,3,'Y'),
              mathutils.Matrix.Rotation(z%360,3,'Z')]
        # print rot_order
        # Standard BVH multiplication order, apply the rotation in the order Z,X,Y
        return (mats[rot_order[2]]*(mats[rot_order[1]]* (mats[rot_order[0]]* MATRIX_IDENTITY_3x3))).to_euler()


    def sunfunc(self, args):
        '''
        Adds a sun
        '''
        x = float(args.pop(0))
        y = float(args.pop(0))
        z = float(args.pop(0))
        bpy.ops.object.light_add(type='SUN')
        #bpy.data.lamps.new('Sun', 'SUN')
        sun = bpy.context.object
        #bpy.context.scene.objects.link(sun)
        c = self.state_color
        sun.color = (c[0],c[1],c[2],1)
        #sun.energy = 5.0
        #sun.specular_factor = 0.5
        vec = mathutils.Vector((x, y, z))
        vec_a = vec.normalized()
        #e_loc = np.array([0,0,0])
        #f_vec = np.array([0,0,-1])
        #r_vec = np.array([1,0,0])
        #u_vec = np.array([0,1,0])
        sun.rotation_euler = self.vecs_to_euler(x,y,z)
        
        
        #light1 = bpy.ops.object.light_add(type='POINT', radius=.001, location=(x, y, z) )
        #light_ob = bpy.context.object
        #light = light_ob.data
        #light.energy = 500
        #light.color = self.state_color

    def pngfunc(self,args):
        width = int(args[0])
        height = int(args[1])
        pngname = args[2]
        scn = bpy.context.scene
        scn.render.resolution_x = width
        scn.render.resolution_y = height
        self.pngname = pngname


    def eyefunc(self,args):
        '''
        Sets eye location eye .3 -.5 -3
        '''
        x = float(args.pop(0))
        y = float(args.pop(0))
        z = float(args.pop(0))

        a = 'camera'
        camera_data = bpy.data.cameras.new(a)
        camera = bpy.data.objects.new(a, camera_data)
        bpy.context.collection.objects.link(camera)
        camera.location = (x,y,z)
        camera.data.lens_unit = 'FOV'
        camera.data.angle = math.radians(76)
        bpy.data.objects[a].show_axis = True
                        
        
    FUNCTION_MAP = {
            "png": pngfunc,
            "color": rgbfunc,
            "sphere": spherefunc,
            "sun": sunfunc,
            "eye": eyefunc,
            }

    def processLines(self, lines):
        linecount=0

        for line in lines:
            linecount = linecount + 1
            print(line)
            the_line = line.split()
            if len(the_line) > 0:
                cmd = the_line.pop(0)
                if cmd == 'break':
                    cmd = the_line.pop(0)
                    breakpoint()
                this_func = self.FUNCTION_MAP.get(cmd)
                if this_func is not None:
                    this_func(self,the_line)

    def savePNG(self):
        pass
 #       bpy.ops.render.render(use_viewport=True)

    def do_raytrace(self):
        pass
    
    def setDefaults(self):
        self.clearScene()
        self.rgbfunc(["1","1","1"])
        self.eyefunc(["0","0","0"])
            
    def read(self,filepath):
        print("running read_some_data...")
        f = open(filepath, 'r', encoding='utf-8')
        self.setDefaults()
        lines = f.readlines()
        self.processLines(lines)
        f.close()
#       self.do_raytrace()
#       self.savePNG()    
 



# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator

def read_cs418_data(context, filepath, use_some_setting):
    print("running read_some_data...")
    lu = cs418Import()
    lu.read(filepath)
    return {'FINISHED'}

class ImportSomeData(Operator, ImportHelper):
    """Import CS418 text scene description file"""
    bl_idname = "import_test.some_data"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import cs418 scene file"

    # ImportHelper mixin class uses this
    filename_ext = ".txt"

    filter_glob: StringProperty(
        default="*.txt",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    use_setting: BoolProperty(
        name="Example Boolean",
        description="Example Tooltip",
        default=True,
    )

#    type: EnumProperty(
#        name="Example Enum",
#        description="Choose between two items",
#        items=(
#            ('OPT_A', "First Option", "Description one"),
#            ('OPT_B', "Second Option", "Description two"),
#        ),
#        default='OPT_A',
#    )

    def execute(self, context):
        return read_cs418_data(context, self.filepath, self.use_setting)


# Only needed if you want to add into a dynamic menu.
def menu_func_import(self, context):
    self.layout.operator(ImportSomeData.bl_idname, text="Import CS418 text file")


# Register and add to the "file selector" menu (required to use F3 search "Text Import Operator" for quick access).
def register():
    bpy.utils.register_class(ImportSomeData)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ImportSomeData)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()

    if len(sys.argv) >=4:
        inputFileName = sys.argv[3]
        read_cs418_data(None, inputFileName, None)
    # test call
    # bpy.ops.import_test.some_data('INVOKE_DEFAULT')
