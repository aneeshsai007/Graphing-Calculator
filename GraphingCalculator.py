# Graphing calculator
from tkinter import * #GUI
from math import * #Used for trig and logs
import copy #Module for deep copying objects
#----------------------------
# This procedure rounds a decimal number to the nearest integer. 
# It takes an input in the form of a float and returns the value in the form of an integer. 
# If the number is greater than 10000000, then it returns 10000000. 
# If the number is less than -10000000, then it returns -10000000. 
#----------------------------
def round_to_nearest(decimal): 

    if decimal > 10000000: return 10000000
    if decimal < -10000000: return -10000000
    round_down = int(decimal)
    if decimal-round_down < 0.5: return round_down
    else: return round_down + 1
    
possible_specials = ["cos","sin","tan","ln","log"] # this is a dictionary of all the special functions
possible_numbers = ["x","p","e","."] # this is a dictionary of numbers
for i in range(10): possible_numbers.append(str(i)) 
possible_ops = ["*","+","/","-","^"] # this is a dictionary five basic operations
dot_width = 8 # assigning the width of the dot to 8
dimensions = ((-8,8),(-8,8)) # x start to x end, y start to y end
fy = 0 # pixels per 1
fx = 0
d= 5 # length of tick marks
h_dot_width = round_to_nearest(dot_width/2)
integrate_precision = 10**3
#----------------------------
# This procedure converts the point that is given to a pixel on the screen.
# It takes in the x and y-coordinates as inputs and displays and displays the output on the graphing screen.
#----------------------------
def point_to_pixel(x_y_tuple): 
    x = round_to_nearest((x_y_tuple[0]-dimensions[0][0])*fx)
    #print("22:",(dimensions[1][1]-x_y_tuple[1])*f,type((dimensions[1][1]-x_y_tuple[1])*f))
    y = round_to_nearest((dimensions[1][1]-x_y_tuple[1])*fy)
    #if x_y_tuple[0] == -5: print(x_y_tuple,"==>",(x,y))
    #print("TRANSFORM:",x_y_tuple,x,y,dimensions)
    return (x,y)

#----------------------------
#This procedure removes spaces in the array raw, and increases the size of the array for each inputted value.
#A value is inputted in the form of the variable i.
#The value of the variable cooked increases by the value of the variable i, and the variable cooked is returned
#----------------------------    
def remove_spaces(raw): # 
    cooked = ""
    for i in raw:
        if i != " ":
            cooked += i
    return cooked

#----------------------------
#This procedure obtains the number of elements in the array. 
#It then inputs the values one by one into the array, thus increasing the length of the array.

def get_num(raw):
    #print("Received number raw:",raw)
    if len(raw)==0:
        raw = "0"
    if raw[0] != "(":
        for i in possible_numbers:
            if raw[0:len(i)] == i:
                return num(raw)
        for i in possible_specials:
            if raw[0:len(i)] == i:
                return num(raw[len(i)+1:len(raw)-1] , i )
    else:
        return convert_to_function(raw[1:len(raw)-1])

#----------------------------
# This procedure converts an array to a function
# It takes an array as an input, and returns the function with parameters nums and ops.
#----------------------------
def convert_to_function(raw_function): 
    print("Raw to convert: " + raw_function)
    nums = []
    ops = []
    op_positions = []
    i=0
    in_brackets = 0
    while i < len(raw_function):
        if raw_function[i] == "(":
            in_brackets += 1
            i += 1
            while in_brackets !=0 and i < len(raw_function) :
                if raw_function[i] == "(": in_brackets+=1
                elif raw_function[i] == ")": in_brackets-=1
                #print("i:",i,"character:",raw_function[i],"in_bracket:",in_brackets)
                i += 1
        if in_brackets == 0 and i<len(raw_function):
            for j in possible_ops:
                if raw_function[i:i+len(j)] == j:
                    ops.append(j)
                    op_positions.append(i)
        i += 1
    #print("Ops in convert to function:",ops)
    if len(ops)==0:
        nums.append(get_num(raw_function))
    else:
        nums.append(get_num(raw_function[:op_positions[0]]))
    for i in range(len(op_positions)-1):
        nums.append(get_num(raw_function[op_positions[i]+1:op_positions[i+1]]))
    if len(ops) != 0:
        nums.append(get_num(raw_function[op_positions[len(op_positions)-1]+1:]))
    
    return function([nums,ops])
	
def close_enough_zero(num):
    if type(num) == str: return False
    margin = float(1/fx)+0.03
    if abs(num) < margin:
        return True
    else: return False
    
class function():
    def __init__(self,f_array,dealt_with=False): # f_array: [ sequence of nums, sequence of ops ]
        self.ops = f_array[1]
        self.nums = f_array[0]
        self.dealt_with = dealt_with
    def clean(self): # remove all dealt_with
        if self.dealt_with: self.dealt_with = False
        for i in self.nums:
            if type(i) == function:
                if i.dealt_with: i.clean()
    def to_str(self):
        func_str = ""
        for i in range(len(self.nums)):
            if type(self.nums[i]) == num:
                func_str += self.nums[i].to_str()
            else:
                func_str += "("+self.nums[i].to_str()+")"
            if i != len(self.nums) - 1:
                func_str += self.ops[i]
        return func_str

    def replace_x(self,what):
        for i in range(len(self.nums)):
            if type(self.nums[i]) == num:
                if self.nums[i].number:
                    if self.nums[i].num == 'x':
                        self.nums[i] = num(copy.deepcopy(what),self.nums[i].operation)
                else:
                    self.nums[i].num.replace_x(what)
            else:
                self.nums[i].replace_x(what)
        return self

    def derivate(self,precision,parent=True):
        duplicate = copy.deepcopy(self).replace_x(function([[num("x"),num("1"),num(str(precision))],["+","/"]]))
        return function([[function([[duplicate,self],["-"]]),num(str(precision))],["*"]])

#----------------------------
# This procedure integrates precision into the calculator, especially for plotting points
    def integrate(self,lower,upper,precision):
        incr = 1/precision
        i = lower
        ans = 0
        while i < upper:
            if self.calc(i) != "undefined" and self.calc(i+incr) != "undefined":
                ans += (self.calc(i)+self.calc(i+incr))*incr/2
            i += incr
        return ans
        
    def pretty_print(self,level=1):
        parent_tab = ""
        tab = ""
        for i in range(level):
            if i > 0: parent_tab += "\t"
            tab += "\t"
        
        print(parent_tab,"Operation Sequence: ")
        for i in self.ops: print(tab,i)
            
        print(parent_tab,"Number Sequence: ")
        for i in self.nums:
            if type(i) == num:
                if i.number:
                    print("\n",tab,"Operation:",i.operation,"; Number:",i.num,end="")
                else:
                    print("\n",tab,"Operation:",i.operation,"; Number:\n",tab,"{")
                    i.num.pretty_print(level+2)
                    print("\n",tab,"}")
            elif type(i) == function:
                print("\n",tab,"Function:",end="")
                if i.dealt_with:
                    print("(Dealt With!)",end="")
                print("\n",tab,"{")
                i.pretty_print(level+2)
                print("\n",tab,"}")
        if level == 1: print("\n")
                
    def calc(self,val):
        new = [ [] , copy.deepcopy(self.ops) ] # nums and ops
        for i in range(len(self.nums)):
            if type(self.nums[i]) == str:
                print(self.nums[i])
            num = self.nums[i].calc(val) #calculates for type num and type function
            if num == "undefined":
                return "undefined"
            else:
                new[0].append(num)
        #if val == -10.0: print("Starting Calculation, x:",val,"; nums:",new[0],"; ops:",new[1])
#----------------------------
#The following is a procedure that integrates the five basic operations into the calculator: addition, subtraction, multiplication, division, and power
#It also takes in the factor of dividing by zero and overflow error, and will not just merely display that the operation is undefined.
#----------------------------
        def reduce(i):
            new[0].pop(i+1)
            new[1].pop(i)
            #if val == -10.0: print("Calculating, x:",val,"; nums:",new[0],"; ops:",new[1])
            return i-1
        try:
            i = 0
            while i < len(new[1]):
                if new[1][i] == "^":
                    new[0][i] **= new[0][i+1]
                    i = reduce(i)
                i+=1
                
            i = 0
            while i < len(new[1]):
                if new[1][i] == "*":
                    new[0][i] *= new[0][i+1]
                    i = reduce(i)
                    
                elif new[1][i] == "/":
                    new[0][i] /= new[0][i+1]
                    i = reduce(i)
                i+=1
                
            i = 0
            while i < len(new[1]):
                if new[1][i] == "-":
                    new[0][i] -= new[0][i+1]
                    i = reduce(i)
                    
                elif new[1][i] == "+":
                    new[0][i] += new[0][i+1]
                    i = reduce(i)
                i+=1
            if(type(new[0][0]) != complex):
                return new[0][0]
            else:
                return "undefined"
        except (ValueError , ZeroDivisionError , TypeError):
            return "undefined"
        except OverflowError:
            return "undefined"
class num():
    def __init__(self,num_given,operation=0):
        self.operation = operation
        if type(num_given) == str:
            for i in range(len(num_given)):
                number = False
                for j in possible_numbers:
                    if num_given[i:i+len(j)] == j:
                        number = True
                        break
                if not number:
                    break
            if number:
                self.num = num_given
                self.number = True
            else:
                self.num = convert_to_function(num_given)
                self.number = False
        elif type(num_given) == function:
            self.number = False
            self.num = num_given
        elif type(num_given) == num:
            self.num = num_given.num
            self.number = num_given.number

    def to_str(self):
        if self.operation == 0:
            if self.number: return self.num
            else: return self.num.to_str()
        else:
            if self.number: return self.operation+"("+self.num+")"
            else: return self.operation+"("+self.num.to_str()+")"   
    
    def calc(self,x=0):
        num = self.num
        if self.num == "p":
            num = pi
        elif self.num == "e":
            num = e
        elif self.num == "x":
            num = x
        if self.number:
            num = float(num)
        else: num = self.num.calc(x)
        try:
            if self.operation == "cos":
                return cos(num)
            elif self.operation == "sin":
                return sin(num)
            elif self.operation == "tan":
                return tan(num)
            elif self.operation == "ln":
                return log(num)
            elif self.operation == "log":
                return log(num,10)
            else: return num
        except (ValueError , ZeroDivisionError , TypeError):
            return "undefined"
        except OverflowError:
            return "undefined"
#----------------------------
#This procedure displays the holes in the graph.
#Whenever the graph is undefined at only a certain point, the procedure will be taken into effect, and the hole will be displayed.
#It takes in the parameters of the previous and current parts of the graph along with the graph dimensions  
#----------------------------      
def hole(prev,current,dimensions): #NEED
    if prev[1] != "undefined" or prev[0] == "undefined": return False
    prev_first_in = prev[0] < dimensions[1][1] and prev[0] > dimensions[1][0]
    if not prev_first_in: return False
    current_in = current < dimensions[1][1] and current > dimensions[1][0]
    if not prev_first_in: return False
    return True

#----------------------------
#This procedure takes in the parameters of the dimension, precisity, roots, function, and the color (which is black).
#It plots the points on the graph with utmost precisity.
#----------------------------

def draw_points(dimensions,precisity,root,function,colour = "black"):
    zero_y = 10
    zeroes = []
    previous_pixel = ("undefined","undefined")
    previous_vals = ["undefined","undefined"]
    x_val = dimensions[0][0]
    while x_val <= dimensions[0][1]:
        y_val = function.calc(x_val)
        #if x_val <-7: print("X:",x_val,";Y:",y_val,";Close Enough",close_enough_zero(y_val))
        if close_enough_zero(y_val):
            not_end_point = x_val != dimensions[0][0] and x_val != dimensions[0][1]
            if len(zeroes) != 0:
                if close_enough_zero(previous_vals[1]) and abs(y_val)<abs(zero_y):
                    if not_end_point:
                        zeroes[-1] = x_val
                        zero_y = y_val
                    else:
                        zeroes.pop(-1)

            if not close_enough_zero(previous_vals[1]) and previous_vals[1] != "undefined" and not_end_point:
                zeroes.append(x_val)
                zero_y = y_val
        if y_val != "undefined":
            pixel = point_to_pixel((x_val,y_val))
            root.create_line(pixel[0],pixel[1],pixel[0],pixel[1]+1,fill=colour,tag="graph")
            if hole(previous_vals,y_val,dimensions):
                graph_dots(root,function,[x_val+(f-2)/precisity],"cyan")
            if previous_pixel[1] != "undefined":
                if previous_pixel[1] - pixel[1] > 1:
                    root.create_line(previous_pixel[0],previous_pixel[1],
                                    previous_pixel[0],pixel[1]-1,fill=colour,tag="graph")

                elif previous_pixel[1] - pixel[1] < -1:
                    root.create_line(previous_pixel[0],previous_pixel[1],
                                    previous_pixel[0],pixel[1]+1,fill=colour,tag="graph")
        else:
            pixel = (x_val,"undefined")
        previous_pixel = pixel
        previous_vals[0] = previous_vals[1]
        previous_vals[1] = y_val

        x_val += 1/precisity
    return zeroes
#----------------------------
# This procedure finds the zeroes of the graph.
# The parameters that are being taken into account are the dimenstions of the graph, precisity of the x-coordinate, and the function)
#----------------------------
def find_zeroes(dimensions,precisity_x,function):
    zero_y = 10
    zeroes = []
    previous = dimensions[1][1]+1
    x = dimensions[0][0]
    while x <= dimensions[0][1]:
        y = function.calc(x)
        #if x_main == 7 or x_main == 8: print("x:",x,"y:",y,"; close_enough:",close_enough_zero(y),"; zeroes:",zeroes)
        if close_enough_zero(y):
            if len(zeroes) != 0:
                if close_enough_zero(previous) and abs(y)<abs(zero_y):
                    if x != dimensions[0][0] and x != dimensions[0][1]:
                        zeroes[-1] = x
                        zero_y = y
                    else:
                        zeroes.pop(-1)
            if not close_enough_zero(previous) and previous != "undefined" and x != dimensions[0][0] and x != dimensions[0][1]:
                zeroes.append(x)
                zero_y = y
        previous = y
        x += 1/precisity_x
    return zeroes

def graph_dots(rootx,func,xs,colour): #This procedure graphs dots and determines how it is placed in relation to pixel width
    for i in xs:
        p = point_to_pixel((i,func.calc(i)))
        rootx.create_oval(p[0]-h_dot_width,p[1]-h_dot_width,p[0]+h_dot_width,p[1]+h_dot_width,fill=colour,tag="graph")

class Control(Frame):
    def __init__(self):
        master = Tk()
        Frame.__init__(self, master=master)
        master.title("Control Panel")
        self.func_input = Entry(master)
        self.func_input.grid(column=2,row=1,columnspan=3)
        Label(master, text = "f(x):").grid(column=1,row=1,rowspan=1)
        self.show_prefs = [["f(x)",IntVar()],["f'(x)",IntVar()],["f\"(x)",IntVar()],
                           ["Extrema",IntVar()],["Inflection",IntVar()]]
        for i in range(len(self.show_prefs)):
            self.show_prefs[i][1].set(True)
            row = 2 + int(i/3)
            Checkbutton(master,text=self.show_prefs[i][0],variable=self.show_prefs[i][1]).grid(column=i%3+1,row=row)
        Label(master, text="Integral Bounds: ").grid(column=1,row=5)
        self.integral_inputs = [Entry(master),Entry(master)]
        for i in range(len(self.integral_inputs)): self.integral_inputs[i].grid(row=5,column=i+2)
        self.integral_ans = StringVar()
        Label(master, textvariable=self.integral_ans).grid(column=3,columnspan=2,row=6)
        Button(master, text = "CALCULATE INTEGRAL", command = self.integrate).grid(column=1,row=7)
        Button(master, text = "CLEAR & GRAPH", command = self.clear_and_graph).grid(column=4,row=7,rowspan=1)
        Button(master, text = "CLEAR", command = self.clear).grid(column=2,row=7,rowspan=1)
        Button(master, text = "GRAPH", command = self.graph).grid(column=3,row=7,rowspan=1)
        Label(master, text = "Settings:").grid(column=1,columnspan=5,row=8)
        Label(master,text = "X Window:").grid(column=1,row=9)
        Label(master,text = "Y Window:").grid(column=1,row=10)
        Button(master, text = "PROBLEM", command = self.problem).grid(column=1,row=11,rowspan=4)
        self.dimensions_input = [[StringVar(),StringVar()],[StringVar(),StringVar()]]
        for i in range(len(self.dimensions_input)):
            for j in range(len(self.dimensions_input[i])):
                Entry(master,textvariable=self.dimensions_input[i][j]).grid(row=9+i,column=2+j)
                self.dimensions_input[i][j].set(j*16-8)
        master.bind("<Return>",lambda s: self.clear_and_graph())
#----------------------------
# This procedure calculates the integral of the function over a certain domain.
# The inputs are the lower and upper x-values, and the output is the answer, which will be displayed onto the screen.
#----------------------------
    def integrate(self):
        raw_function = remove_spaces(self.func_input.get().lower())
        self.func = convert_to_function(raw_function)
        ans = self.func.integrate(int(self.integral_inputs[0].get()),int(self.integral_inputs[1].get()),integrate_precision)
        self.integral_ans.set(str(ans))
        print("INTEGRAL ANSWER:",ans)
        
    def clear(self): # This procedure clears the graph
        rootx.delete("graph")
        dimensions = self.initialise_graphs()

    def clear_and_graph(self): # This procedure first clears the graph then graphs the new function
        self.clear()
        self.graph()

    def initialise_graphs(self):
        rootx.delete("axes")
        global w,h,fx,fy,dimensions
        dimensions = [[0,0],[0,0]]
        for i in range(len(self.dimensions_input)):
            for j in range(len(self.dimensions_input[i])): dimensions[i][j] = float(self.dimensions_input[i][j].get())
        w = 800
        h = 800
        fx = w / (dimensions[0][1]-dimensions[0][0])
        fy = h / (dimensions[1][1]-dimensions[1][0])
        print("D:",dimensions,fx,fy,w,h)
        rootx.configure(width = w,height = h)
        if dimensions[0][1] >= 0 and dimensions[0][0] <= 0: #then draw y axis
            points = [point_to_pixel((0,dimensions[1][0])),point_to_pixel((0,dimensions[1][1]))]
            rootx.create_line(points[0][0],points[0][1],points[1][0],points[1][1],tag="axes")
            #print(points[0][0],points[0][1],points[1][0],points[1][1],dimensions,point_to_pixel((0,dimensions[1][0])))
            for i in range(round_to_nearest(dimensions[1][0]),round_to_nearest(dimensions[1][1])):
                pixel = point_to_pixel((0,i))
                #print(pixel)
                rootx.create_line(pixel[0]-d/2,pixel[1],pixel[0]+d/2,pixel[1],tag="axes")
                
        if dimensions[1][1] >= 0 and dimensions[1][0] <= 0: #then draw x axis
            points = [point_to_pixel((dimensions[0][0],0)),point_to_pixel((dimensions[0][1],0))]
            rootx.create_line(points[0][0],points[0][1],points[1][0],points[1][1],tag="axes")
            for i in range(round_to_nearest(dimensions[0][0]),round_to_nearest(dimensions[0][1])):
                pixel = point_to_pixel((i,0))
                print(pixel)
                rootx.create_line(pixel[0],pixel[1]-d/2,pixel[0],pixel[1]+d/2,tag="axes")
        rootx.pack()
        ans = ""
        return dimensions
        
    def graph(self):
        global fx, fy
        raw_function = remove_spaces(self.func_input.get().lower())
        self.func = convert_to_function(raw_function)
        self.func.pretty_print()
        print("f(-2) =",self.func.calc(-2))
        print("f(0) =",self.func.calc(0))
        print("f(100) =",self.func.calc(100))
        if self.show_prefs[0][1].get(): draw_points(dimensions,fx,rootx,self.func)
        derivative = self.func.derivate(10**8) # not higher than 10^8
        print("\nDERVIVATIVE:")
        print("y' =",derivative.to_str())
        derivative.pretty_print()
        print("f'(-2) =",derivative.calc(-2))
        print("f'(0) =",derivative.calc(0))
        print("f'(100) =",derivative.calc(100))
        if self.show_prefs[1][1].get(): extr = draw_points(dimensions,fx,rootx,derivative,"blue")
        else: extr = find_zeroes(dimensions,fx,derivative)
        if self.show_prefs[3][1].get(): graph_dots(rootx,self.func,extr,"red")
        print("\nSECOND DERIVATIVE:")
        second = derivative.derivate(10**3)
        # idealy precision in this should be way less precision than in the first derivative
        #second.pretty_print()
        print("y\" =",second.to_str())
        if self.show_prefs[2][1].get(): inflections = draw_points(dimensions,fx,rootx,second,"maroon")
        else: inflections = find_zeroes(dimensions,fx,second)
        print("Inflections:",inflections)
        if self.show_prefs[4][1].get(): graph_dots(rootx,self.func,inflections,"purple")
    def problem(self):
        with open("grapherProblems.txt","a") as problem_file:
            problem_file.write(self.func_input.get()+"\n")
control_panel = Control()
root_master = Tk()
rootx = Canvas(master = root_master)
root_master.title("Graph")
control_panel.initialise_graphs()
control_panel.mainloop()
