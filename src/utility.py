import bpy
import os
import math
import mathutils
import random
from math import radians
import bmesh
import random
import csv



class Factory:
    #######################################################################################################################
    ##################### Constants #######################################################################################
    
    #Bottom

    BOTTOM_DIA = 4
    BOTTOM_HEIGHT = 3
    SUB_BOTTOM_DIA = 1
    SUB_BOTTOM_INNER_DEPTH = 0.5
    ##Bolt
    BOLT_RAD = 0.4
    BOLT_LENGTH = 1.4
    BOLT_BIT_DIA = 0.2
    BOLT_THREAD_LENGTH = 1.4
    BOLT_THREAD_DIA = 0.2
    
    BOARD_THICKNESS = 0.1
    FOUR_CYL_DIA = 0.7

    C1_LENGTH = 0
    C2_LENGTH = 0
    C3_LENGTH = 0
    C4_LENGTH = 0
    C5_LENGTH = 0

    EXTENSION_THICKNESS = 0.2
    


    #######################################################################################################################
    ####################### Variable ######################################################################################
    
    #Position of Motor
    init_x = 0
    init_y = 0
    init_z = 0

    #Size of bottom part
    bottom_length = 6.4
    inner_radius = 1

    #Bolts
    bolt_ortientation = False
    bit_type = "Torx"
    bolt_num = 0
    gear_orientation = "mf_zero"

    
    # Define the behavior of rotation and flip
    orient_dict = {
        'mf_zero':((radians(0),"Z"), BOTTOM_DIA, -BOTTOM_HEIGHT-0.1),
        'mf_Ninety':((radians(-90),"Z"), BOTTOM_HEIGHT, BOTTOM_HEIGHT),
        'mf_HundredEighteen':((radians(-180),"Z"), BOTTOM_DIA, BOTTOM_DIA),
        'mf_TwoHundredSeven':((radians(-270),"Z"), BOTTOM_HEIGHT, -BOTTOM_DIA)
    }

    #Extention Zone
    head_Type = None
    ex_type = None

    #Color Render
    color_render = False
    gear_Flip = False

    #Save path
    motor_param = [
        "mf_Head_Type",
        "mf_Extension_Type",
        "mf_Gear_Orientation",
        "mf_Flip",
        "mf_Color_Render",
        "mf_Bottom_Length",
        "mf_Sub_Bottom_Length",

        "mf_Bit_Type",
        "mf_Bolt_Orientation",
        
    ]
    key_list = []
    save_path = "None"
    id_Nr = 0
    s_bolt_list = []
    l_bolt_list = []
    bolt_position = []
    out_bolt_position = []

    def __init__(self,factory):
        self.head_Type = factory.mf_Head_Type
        self.init_x = factory.init_x
        self.init_y = factory.init_y
        self.init_z = factory.init_z
        self.bottom_length = factory.mf_Bottom_Length
        self.inner_radius = 0.5
        self.sub_bottom_length = factory.mf_Sub_Bottom_Length
        self.bolt_ortientation = factory.mf_Bolt_Orientation

        self.bit_type = factory.mf_Bit_Type
        self.bolt_position = []
        self.out_bolt_position = []


        self.gear_Flip = factory.mf_Flip

        self.lower_gear_dia = factory.mf_Lower_Gear_Dia
        self.lower_gear_position = factory.mf_Lower_Gear_Position
        
        self.color_render = factory.mf_Color_Render


        self.save_path = factory.save_path
        self.id_Nr = factory.id_Nr    
        self.init_modify(factory)
    
    def init_modify(self,factory):
        pass

    ##############################################################################################################################
    ########################## Utility ###########################################################################################
    

    def combine_all_obj(self, main_obj, object_list):
        bpy.ops.object.select_all(action='DESELECT')
        #bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.view_layer.objects.active = main_obj
        for obj in object_list:
            try:
                if obj is None:
                    continue
                main_obj.select_set(True)        
                obj.select_set(True)
                bpy.ops.object.join()
            except ReferenceError:
                bpy.context.view_layer.objects.active = None
                return main_obj
        bpy.context.view_layer.objects.active = None
        return main_obj

    def rotate_around_point(self, origin, Angle, obj_position):
        if type(Angle) == int or float:
            rot = radians(Angle)   
        else:
            rot = Angle
        relativ_point = [obj_position[0]-origin[0], obj_position[1]-origin[1]]
        x = relativ_point[0] * math.cos(rot) - relativ_point[1] * math.sin(rot) 
        y = relativ_point[0] * math.sin(rot)  + relativ_point[1] * math.cos(rot)
        return x+origin[0],y+origin[1]

    def create_ring(self, position,height,radius,thickness):
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=height, location=position)
        cly_out = bpy.context.object
        bpy.ops.mesh.primitive_cylinder_add(radius=radius-thickness, depth=height+1, location=position)
        cly_in = bpy.context.object

        bool_in = cly_out.modifiers.new('bool_in', 'BOOLEAN')
        bool_in.operation = 'DIFFERENCE'
        bool_in.object = cly_in
        bpy.context.view_layer.objects.active = cly_out
        res = bpy.ops.object.modifier_apply(modifier='bool_in')
        # Delete the cylinder.x
        cly_in.select_set(True)
        bpy.ops.object.delete() 
        #if rotation is not None:
        #    bpy.context.view_layer.objects.active = cly_out
        #    bpy.ops.transform.rotate(value=rotation[0],orient_axis=rotation[1]) 
        return cly_out

    def add_mesh(self, name, verts, faces, edges=None, col_name="Collection"):    
        if edges is None:
            edges = []
        mesh = bpy.data.meshes.new(name)
        obj = bpy.data.objects.new(mesh.name, mesh)
        col = bpy.data.collections.get(col_name)
        col.objects.link(obj)
        bpy.context.view_layer.objects.active = obj
        mesh.from_pydata(verts, edges, faces)
        return obj

    def add_torx(self,position,size,depth):
        x = position[0]
        y = position[1]
        z = position[2] + 0.2
        depth += 0.1

        v1 = [0, 0.5 * size,0]
        v2 = [- 0.1443 * size, 0.25 * size,0]
        v3 = [- 0.433 * size, 0.25 * size, 0]
        v4 = [-0.2887 * size, 0, 0]
        v5 = [- 0.433 * size,  -0.25 * size, 0]
        v6 = [-0.1443 * size, -0.25 * size, 0]

        verts = [
            self.add_vector(position, v1),
            self.add_vector(position, v2),
            self.add_vector(position, v3),
            self.add_vector(position, v4),
            self.add_vector(position, v5),
            self.add_vector(position, v6),
            self.add_vector(position, v1,minus=1),
            self.add_vector(position, v2,minus=1),
            self.add_vector(position, v3,minus=1),
            self.add_vector(position, v4,minus=1),
            self.add_vector(position, v5,minus=1),
            self.add_vector(position, v6,minus=1),

            self.add_vector(position, v1, height=depth),
            self.add_vector(position, v2, height=depth),
            self.add_vector(position, v3, height=depth),
            self.add_vector(position, v4, height=depth),
            self.add_vector(position, v5, height=depth),
            self.add_vector(position, v6, height=depth),
            self.add_vector(position, v1,minus=1, height=depth),
            self.add_vector(position, v2,minus=1, height=depth),
            self.add_vector(position, v3,minus=1, height=depth),
            self.add_vector(position, v4,minus=1, height=depth),
            self.add_vector(position, v5,minus=1, height=depth),
            self.add_vector(position, v6,minus=1, height=depth),
            [x,y,z-depth*2],
        ]
        
        up = [0,1,2,3,4,5,6,7,8,9,10,11]
        bott = [12,13,14,15,16,17,18,19,20,21,22,23]
        faces = [up]
        for i in range(12):
            if i < 11:
                faces.append([up[i],up[i+1],bott[i+1],bott[i]])
                faces.append([bott[i+1],bott[i],24])
            else:
                faces.append([up[11],up[0],bott[0],bott[11]])
                faces.append([bott[11],bott[0],24])
        
        obj = self.add_mesh("torx", verts, faces)
        return obj

    def diff_obj(self, main, slave):
        boolean = main.modifiers.new('bool_in', 'BOOLEAN')
        boolean.operation = 'DIFFERENCE'
        boolean.object = slave
        bpy.context.view_layer.objects.active = main
        res = bpy.ops.object.modifier_apply(modifier='bool_in')
        
        return res

    def add_vector(self,v1,v2,minus=0,height=0):
        out = []
        for i in range(len(v1)):
            if minus == 1:
                out.append(v1[i]-v2[i])
            else:
                out.append(v1[i]+v2[i])
        if height != 0:
            out[-1] -= height
        return out

    def create_motor_main(self, position, height, width, length):

        # Add main cylinder
        cylinder_r = width/2
        cylinder_d = length

        bpy.ops.mesh.primitive_cylinder_add(radius=cylinder_r, depth=cylinder_d, location=position)
        cyl = bpy.context.object
        cyl.name = 'Motor_main_part'


        # Add cube 1
        cuboid_lx = position[0] - width- height/2
        cuboid_ly = position[1]
        cuboid_lz = position[2]
        bpy.ops.mesh.primitive_cube_add(location=(cuboid_lx,cuboid_ly,cuboid_lz))
        bpy.ops.transform.resize(value=(width, width, length))

        cube_1 = bpy.context.object
        cube_1.name = 'cube1'

        # Add cube 2
        cuboid_lx = position[0] + width + height/2
        cuboid_ly = position[1]
        cuboid_lz = position[2]
        bpy.ops.mesh.primitive_cube_add(location=(cuboid_lx,cuboid_ly,cuboid_lz))
        bpy.ops.transform.resize(value=(width, width, length))

        cube_2 = bpy.context.object
        cube_2.name = 'cube2'


        # Boolean Operation for Cube 1
        bool_1 = cyl.modifiers.new('bool_1', 'BOOLEAN')
        bool_1.operation = 'DIFFERENCE'
        bool_1.object = cube_1
        bpy.context.view_layer.objects.active = cyl
        res = bpy.ops.object.modifier_apply(modifier='bool_1')

        # Boolean Operation for Cube 2
        bool_2 = cyl.modifiers.new('bool_2', 'BOOLEAN')
        bool_2.operation = 'DIFFERENCE'
        bool_2.object = cube_2
        bpy.context.view_layer.objects.active = cyl
        res = bpy.ops.object.modifier_apply(modifier='bool_2')

        cube_2.select_set(True)
        bpy.ops.object.delete()

        cube_1.select_set(True)
        bpy.ops.object.delete()

        return cyl

    def create_bolt(self, position,rotation=None,only_body=False):
        """[summary]
        create_bolt((0,0,0),(radians(45),'X'))
        """   
        bit_type = self.bit_type
        orientation = self.bolt_ortientation
        out_dia = self.BOLT_RAD
        if only_body :
            out_length = 0.3
            z_in = position[2] + out_length/2 - 0.15

            part = self.create_ring((position[0],position[1],z_in),out_length, out_dia,0.2*out_dia)
            part.name = 'Bolt'

            if rotation:
                bpy.ops.object.select_all(action='DESELECT')
                part.select_set(True)
                bpy.ops.transform.rotate(value=rotation[0],orient_axis=rotation[1]) 
            return [part, None]

        else:
            out_length = self.BOLT_LENGTH

            in_dia = 0.8 * self.BOLT_RAD
            
            #Create first BIt base of Bolt
            z_in = position[2] + out_length/2
            bpy.ops.mesh.primitive_cylinder_add(radius=in_dia, depth=in_dia, location=(position[0],position[1],z_in))
            in_cyl = bpy.context.object
            in_cyl.name = 'in_cylinder'

            #Create Thread of Bolt

            bpy.ops.mesh.primitive_cylinder_add(radius=self.BOLT_THREAD_DIA, depth=self.BOLT_THREAD_LENGTH, location=position)
            thread = bpy.context.object
            thread.name = 'thread'

            z_sphe = z_in + in_dia/2

            #Create Shell for Bolt
            out_cyl = self.create_ring(position, out_length, out_dia, 0.2)
            #bpy.ops.mesh.primitive_cylinder_add(radius=out_dia, depth=out_length, location=position)
            #out_cyl = bpy.context.object
            out_cyl.name = 'out_cylinder'

            bpy.ops.mesh.primitive_uv_sphere_add(radius=in_dia, location=(position[0],position[1],z_sphe))
            sphere = bpy.context.object
            sphere.name = 'sphere'
            z_cut = z_sphe + in_dia/2 + in_dia/3
            bpy.ops.mesh.primitive_cylinder_add(radius=in_dia, depth=in_dia, location=(position[0],position[1],z_cut))
            cut_cyl = bpy.context.object
            cut_cyl.name = 'cut_cylinder'

            bool_in = sphere.modifiers.new('bool_in', 'BOOLEAN')
            bool_in.operation = 'DIFFERENCE'
            bool_in.object = cut_cyl
            bpy.context.view_layer.objects.active = sphere
            res = bpy.ops.object.modifier_apply(modifier='bool_in')
            # Delete the cylinder.x
            cut_cyl.select_set(True)
            bpy.ops.object.delete() 

            if bit_type == 'mf_Bit_Slot':
                bpy.ops.mesh.primitive_cube_add(location=(position[0],position[1],z_sphe+ in_dia/3))
                bpy.ops.transform.resize(value=(in_dia*1.5, 0.05, 0.2))
                bit = bpy.context.object
            elif bit_type == 'mf_Bit_Torx':
                bit = self.add_torx((position[0],position[1],z_sphe+ in_dia),in_dia*1.5,0.2)
            elif bit_type == 'mf_Bit_Cross':
                bpy.ops.mesh.primitive_cube_add(location=(position[0],position[1],z_sphe+ in_dia/3))
                bpy.ops.transform.resize(value=(0.05, in_dia, 0.2))
                bit_1 = bpy.context.object
                bool_bit = sphere.modifiers.new('bool_bit', 'BOOLEAN')
                bool_bit.operation = 'DIFFERENCE'
                bool_bit.object = bit_1
                bpy.context.view_layer.objects.active = sphere
                res_2 = bpy.ops.object.modifier_apply(modifier='bool_bit')

                bool_bit_2 = in_cyl.modifiers.new('bool_bit_2', 'BOOLEAN')
                bool_bit_2.operation = 'DIFFERENCE'
                bool_bit_2.object = bit_1
                bpy.context.view_layer.objects.active = in_cyl
                res_2 = bpy.ops.object.modifier_apply(modifier='bool_bit_2')

                bool_bit_3 = out_cyl.modifiers.new('bool_bit_3', 'BOOLEAN')
                bool_bit_3.operation = 'DIFFERENCE'
                bool_bit_3.object = bit_1
                bpy.context.view_layer.objects.active = out_cyl
                res_2 = bpy.ops.object.modifier_apply(modifier='bool_bit_3')

                bit_1.select_set(True)
                bpy.ops.object.delete() 
                #bpy.ops.transform.rotate(value=radians(90),orient_axis='Z') 

                bpy.ops.mesh.primitive_cube_add(location=(position[0],position[1],z_sphe+ in_dia/3))
                bpy.ops.transform.resize(value=(in_dia, 0.05, 0.2))
                bit_2 = bpy.context.object   
                bool_bit = sphere.modifiers.new('bool_bit', 'BOOLEAN')
                bool_bit.operation = 'DIFFERENCE'
                bool_bit.object = bit_2
                bpy.context.view_layer.objects.active = sphere
                res_2 = bpy.ops.object.modifier_apply(modifier='bool_bit')

                bool_bit_2 = in_cyl.modifiers.new('bool_bit_2', 'BOOLEAN')
                bool_bit_2.operation = 'DIFFERENCE'
                bool_bit_2.object = bit_2
                bpy.context.view_layer.objects.active = in_cyl
                res_2 = bpy.ops.object.modifier_apply(modifier='bool_bit_2')

                bool_bit_3 = out_cyl.modifiers.new('bool_bit_3', 'BOOLEAN')
                bool_bit_3.operation = 'DIFFERENCE'
                bool_bit_3.object = bit_2
                bpy.context.view_layer.objects.active = out_cyl
                res_2 = bpy.ops.object.modifier_apply(modifier='bool_bit_3')

                bit_2.select_set(True)
                bpy.ops.object.delete()          

            if bit_type == 'mf_Bit_Cross':
                pass
            
            else:
                bool_bit = sphere.modifiers.new('bool_bit', 'BOOLEAN')
                bool_bit.operation = 'DIFFERENCE'
                bool_bit.object = bit
                bpy.context.view_layer.objects.active = sphere
                res_2 = bpy.ops.object.modifier_apply(modifier='bool_bit')

                bool_bit_2 = in_cyl.modifiers.new('bool_bit_2', 'BOOLEAN')
                bool_bit_2.operation = 'DIFFERENCE'
                bool_bit_2.object = bit
                bpy.context.view_layer.objects.active = in_cyl
                res_2 = bpy.ops.object.modifier_apply(modifier='bool_bit_2')

                bool_bit_3 = out_cyl.modifiers.new('bool_bit_3', 'BOOLEAN')
                bool_bit_3.operation = 'DIFFERENCE'
                bool_bit_3.object = bit
                bpy.context.view_layer.objects.active = out_cyl
                res_2 = bpy.ops.object.modifier_apply(modifier='bool_bit_3')

                bit.select_set(True)
                bpy.ops.object.delete() 

            if self.color_render:
                self.rend_color(out_cyl,"Plastic")
                self.rend_color(sphere,"Bit")
                self.rend_color(in_cyl,"Bit")
                self.rend_color(thread,"Bit")
            bolt = self.combine_all_obj(thread,[sphere,in_cyl])
            bolt.name = 'Bolt_'+str(self.bolt_num)
            self.bolt_num+=1
            #self.save_modell(bolt)
            #part = self.combine_all_obj(out_cyl,[bolt])


        if orientation == 'mf_all_random':
            Angle = random.randrange(0, 360, 10) 
            bpy.ops.object.select_all(action='DESELECT')
            bolt.select_set(True)    
            bpy.ops.transform.rotate(value=radians(Angle),orient_axis='Z') 
        if rotation:
            bpy.ops.object.select_all(action='DESELECT')
            out_cyl.select_set(True)
            bolt.select_set(True)
            bpy.ops.transform.rotate(value=rotation[0],orient_axis=rotation[1]) 
        self.bolt_position.append(position)
        return [out_cyl,bolt]

    def rend_color(self, obj, part):

        mat = bpy.data.materials.new(name="Material")
        
        if part == "Metall":
            mat.metallic = 0.8
            mat.roughness = 0.4
            mat.diffuse_color = (0.3, 0.3, 0.3, 1)
            mat.specular_intensity = 0.9
        
        elif part == "Energy":
            mat.diffuse_color = (0.781, 0.775, 0.308, 1)
        
        elif part == "Plastic":
            mat.diffuse_color = (0, 0, 0, 1)
            mat.metallic = 0.4
            mat.specular_intensity = 0.5
            mat.roughness = 0.7

        elif part == "Bit":
            mat.diffuse_color = (0.9, 0.9, 0.9, 1)
            mat.metallic = 0.85
            mat.specular_intensity = 0.5
            mat.roughness = 0.1

        # Assign it to object
        if obj.data.materials:
            # assign to 1st material slot
            obj.data.materials[0] = mat
        else:
            # no slots
            obj.data.materials.append(mat)
        bpy.context.view_layer.objects.active = None

    def rotate_object(self, object_rotate):
        rotation, length_relativ, mirror = self.orient_dict[self.gear_orientation]
        x,y,z = object_rotate.location
        bpy.ops.object.select_all(action='DESELECT')
        object_rotate.select_set(True)
        #bpy.context.view_layer.objects.active = object_rotate
        if self.gear_orientation == 'mf_HundredEighteen' :
            nx,ny = self.rotate_around_point((0,0),180,(x,y))
            bpy.ops.transform.translate(value=(nx-x,ny-y,0))
            bpy.ops.transform.rotate(value=-radians(180),orient_axis=rotation[1])

        elif self.gear_orientation == 'mf_TwoHundredSeven' :
            nx,ny = self.rotate_around_point((0,0),-270,(x,y))
            bpy.ops.transform.translate(value=(nx-x,ny-y,0))
            bpy.ops.transform.rotate(value=-rotation[0],orient_axis=rotation[1])

        elif self.gear_orientation == 'mf_Ninety' :
            nx,ny = self.rotate_around_point((0,0),-90,(x,y))
            bpy.ops.transform.translate(value=(nx-x,ny-y,0))
            bpy.ops.transform.rotate(value=-rotation[0],orient_axis=rotation[1])

        else:
            pass

    def init_key_list(self,factory):
        key_list = ["Nr."]
        for name in dir(factory):
            if name[0:3] == "mf_":
                key_list.append(name)
        key_list.append("Bolts_Positions")
        self.key_list=key_list

    def init_csv(self,path, factory):
        self.init_key_list(factory)
        with open(path, "a+", encoding='utf-8') as log:
            writer = csv.writer(log)
            writer.writerow(self.key_list)

    def write_data(self, path, data, factory):

        csvdict = csv.DictReader(open(path, 'rt', encoding='utf-8', newline=''))
        dictrow = [row for row in csvdict if len(row) > 0 ]
        dictrow.append(data)
        with open(path, "w+", encoding='utf-8', newline='') as lloo:
            # lloo.write(new_a_buf.getvalue())
            wrier = csv.DictWriter(lloo, self.key_list)
            wrier.writeheader()
            for wowow in dictrow:
                wrier.writerow(wowow)

    def save_csv(self, factory):
        if self.save_path == "None":
            pass
        else:
            self.init_key_list(factory)

            csv_path= self.save_path + 'data.csv'
            if not os.path.isfile(csv_path):
                self.init_csv(csv_path, factory)                             
            data = self.create_data_list(factory)
            self.write_data(csv_path,data, factory)

    def create_data_list(self, factory):
        data_list=[str(self.id_Nr)]
        
        for name in dir(factory):
            if name[0:3] == "mf_":
                if name in self.motor_param:
                    data_list.append(getattr(factory,name))
                else:
                    data_list.append('-')
        data_list.append(self.bolt_position)
        data = dict(zip(self.key_list,data_list))
        return data

    def save_modell(self,modell, addtional = None):
        
        if self.save_path == "None":
            pass
        else:

            if modell is None:
                return     
            path_of_folder = self.save_path + str(self.id_Nr)+'/'
            bpy.ops.object.select_all(action='DESELECT')
            modell.select_set(True)
            if addtional:
                addtional.select_set(True)
            name = modell.name
            if name == "Bolt" and os.path.isfile(path_of_folder+name+'.stl'):
                return
            try:
                bpy.ops.export_mesh.stl(filepath=path_of_folder+name+'.stl', check_existing=True, use_selection=True, filter_glob='*.stl',)
            except:
                print("Error!")
            bpy.ops.object.select_all(action='DESELECT')

    def calculate_bolt_position(self,root_position):
        x ,y, z = root_position
        position=[]
        rotation, length_relativ, mirror = self.orient_dict[self.gear_orientation]
        self.out_bolt_position += self.bolt_position[0:2]
        for b_position in self.bolt_position[2:]:
            x_new, y_new = self.rotate_around_point((x,y),rotation[0],(b_position[0],b_position[1]))
            if self.gear_Flip:
                x_new = x- x_new
                y_new = y - y_new
                if self.gear_orientation in ['mf_zero','mf_HundredEighteen']:
                    x_new -= 2*x
                    
                else:
                    y_new -= 2*y
            position.append((x_new, y_new, b_position[2]))
        self.out_bolt_position = position