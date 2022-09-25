# -*- coding: utf-8 -*-

# python imports
from math import degrees

# pyfuzzy imports
from fuzzy.storage.fcl.Reader import Reader
import numpy as np
import math
class FuzzyController:

    def __init__(self, fcl_path):
        self.system = Reader().load_from_file(fcl_path)


    def _make_input(self, world):
        return dict(
            cp = world.x,
            cv = world.v,
            pa = degrees(world.theta),
            pv = degrees(world.omega)
        )


    def _make_output(self):
        return dict(
            force = 0.
        )

    def getSets(self, theClass):
        method_list = []
        for attribute in dir(theClass):
            attribute_value = getattr(theClass, attribute)
            if callable(attribute_value):
                if attribute.startswith('__') == False:
                    method_list.append(attribute)
        return method_list

    def get_memberships(self,input, argument):
        method_list = self.getSets(argument.__class__)
        member_dic = {}
        for i in method_list:
            member_dic[i]= getattr(argument.__class__, i)(argument, input)
        return member_dic

    def fuzzify(self, input):
        fuzzified_input = {}
        pa_fuzzi = self.Pa_Fuzzifier()
        fuzzified_input['pa'] = self.get_memberships(input['pa'], pa_fuzzi)

        pv_fuzzi = self.Pv_Fuzzifier()
        fuzzified_input['pv'] = self.get_memberships(input['pv'], pv_fuzzi)

        #bonus
        cv_fuzzi = self.Cv_Fuzzifier()
        fuzzified_input['cv'] = self.get_memberships(input['cv'], cv_fuzzi)

        cp_fuzzi = self.Cp_Fuzzifier()
        fuzzified_input['cp'] = self.get_memberships(input['cp'], cp_fuzzi)

        return fuzzified_input

    def infer(self, fuzzified_input):
        inferer = self.Rules()
        inferences = inferer.infer(fuzzified_input)
        return inferences

    def calculate_force_membership(self, x, infered_values):
        force = self.Forces(infered_values)
        force_memberships = self.get_memberships(x, force)
        x_membership = max(force_memberships.values())
        return x_membership

    def center_of_gravity(self, infered_values):
        force_points = np.linspace(-100, 100, 2000)
        dx = force_points[1] - force_points [0]
        integral = 0
        denominator = 0
        for point in force_points:
            u = self.calculate_force_membership(point, infered_values)
            integral+= u * point * dx
            denominator += u * dx
        if denominator==0:
            return 0

        return float(integral/denominator)

    def decide(self, world):
        fuzzified_input = self.fuzzify(self._make_input(world))

        infered = self.infer(fuzzified_input)
        # print(self._make_input(world))
        forcee = self.center_of_gravity(infered)
        output = self._make_output()
        self.system.calculate(self._make_input(world), output)
        #force = self.myCalculate(self._make_input(world))
        print("force: "+str(forcee))
        # print("force = "+ str(output['force']))
        return forcee


    class Pa_Fuzzifier:
         def __init__(self):
             pass

         def up_more_right(self, x):
             if 0 <= x < 30:
                 return x/30
             if 30 <= x <= 60:
                return (-x/30) + 2
             return 0

         def up_right(self, x):
             if 30 <= x < 60:
                 return (x / 30) - 1
             if 60 <= x <= 90:
                 return (-x / 30) + 3
             return 0

         def up(self, x):
             if 60 <= x < 90:
                 return (x / 30) - 2
             if 90 <= x <= 120:
                 return (-x / 30) + 4
             return 0

         def up_left(self, x):
             if 90 <= x < 120:
                 return (x / 30) - 3
             if 120 <= x <= 150:
                 return (-x / 30) + 5
             return 0

         def up_more_left(self, x):
             if 120 <= x < 150:
                 return (x / 30) - 4
             if 150 <= x <= 180:
                 return (-x / 30) + 6
             return 0

         def down_more_left(self, x):
             if 180 <= x < 210:
                 return (x / 30) - 6
             if 210 <= x <= 240:
                 return (-x / 30) + 8
             return 0

         def down_left(self, x):
             if 210 <= x < 240:
                 return (x / 30) - 7
             if 240 <= x <= 270:
                 return (-x / 30) + 9
             return 0

         def down(self, x):
             if 240 <= x < 270:
                 return (x / 30) - 8
             if 270 <= x <= 300:
                 return (-x / 30) + 10
             return 0

         def down_right(self, x):
             if 270 <= x < 300:
                 return (x / 30) - 9
             if 300 <= x <= 330:
                 return (-x / 30) + 11
             return 0

         def down_more_right(self, x):
             if 300 <= x < 330:
                 return (x / 30) - 10
             if 330 <= x <= 360:
                 return (-x / 30) + 12
             return 0


    class Pv_Fuzzifier:
         def __init__(self):
             pass

         def cw_fast(self, x):
             if x < -200:
                 return 1
             if -200 <= x <= -100:
                 return -x/100 - 1
             return 0

         def cw_slow(self, x):
             if -200 <= x < -100:
                 return (x / 100) + 2
             if -100 <= x <= 0:
                 return (-x / 100)
             return 0

         def stop(self, x):
             if -100 <= x < 0:
                 return (x / 100) + 1
             if 0 <= x <= 100:
                 return (-x / 100) + 1
             return 0

         def ccw_slow(self, x):
             if 0 <= x < 100:
                 return (x / 100)
             if 100 <= x <= 200:
                 return (-x / 100) + 2
             return 0

         def ccw_fast(self, x):
             if x > 200:
                 return 1
             if 100 <= x <= 200:
                 return (x / 100) - 1
             return 0

    class Cv_Fuzzifier:
        def __init__(self):
            pass

        def left_fast(self, x):
            if -5 <= x <= -2.5:
                return -x / 2.5 - 1
            return 0

        def left_slow(self, x):
            if -5 <= x < -1:
                return x / 4 + 1.25
            if -1<= x <= 0:
                return -x
            return 0

        def stop(self, x):
            if -1 <= x < 0:
                return x + 1
            if 0<= x <= 1:
                return -x + 1
            return 0

        def right_slow(self, x):
            if 0 <= x < 1:
                return x
            if 1<= x <= 5:
                return -x/4 + 1.25
            return 0

        def right_fast(self, x):
            if 2.5 <= x <= 5:
                return x / 2.5 - 1
            return 0

    class Cp_Fuzzifier:
        def __init__(self):
            pass

        def left_far(self, x):
            if -10 <= x <= -5:
                return -x / 5 - 1
            return 0

        def left_near(self, x):
            if -10 <= x < -2.5:
                return x / 7.5 + 4/3
            if -2.5 <= x <= 0:
                return -x/ 2.5
            return 0

        def stop(self, x):
            if -2.5 <= x < 0:
                return x/2.5 + 1
            if 0 <= x <= 2.5:
                return -x/2.5 + 1
            return 0

        def right_near(self, x):
            if 0 <= x < 2.5:
                return x/2.5
            if 2.5 <= x <= 10:
                return -x / 7.5 + 4/3
            return 0

        def right_far(self, x):
            if 5 <= x <= 10:
                return x / 5 - 1
            return 0


    class Forces:
        def __init__(self, infered_values):
            self.infered_values = infered_values
        def left_fast(self, x):
            membership = 0
            if -100 <= x < -80:
                membership = (x / 20) + 5
            if -80 <= x <= -60:
                membership = (-x / 20) -3
            return min(membership, self.infered_values['left_fast'])

        def left_slow(self, x):
            membership = 0
            if -80 <= x < -60:
                membership = (x / 20) + 4
            if -60 <= x <= 0:
                membership = (-x / 60)
            return min(membership, self.infered_values['left_slow'])

        def stop(self, x):
            membership = 0
            if -60 <= x < 0:
                membership = (x / 60) + 1
            if 0 <= x <= 60:
                membership = (-x / 60) + 1
            return min(membership, self.infered_values['stop'])

        def right_slow(self, x):
            membership = 0
            if 0 <= x < 60:
                membership = (x / 60)
            if 60 <= x <= 80:
                membership = (-x / 20) + 4
            return min(membership, self.infered_values['right_slow'])

        def right_fast(self, x):
            membership = 0
            if 60 <= x < 80:
                membership = (x / 20) - 3
            if 80 <= x <= 100:
                membership = (-x / 20) + 5
            return min(membership, self.infered_values['right_fast'])

    class Rules:
        def __init__(self):
             pass

        def infer(self, input):
            pa = input['pa']
            pv = input['pv']
            cp = input['cp']
            cv = input['cv']
            forces = {}
            force_terms = ['left_fast', 'left_slow', 'stop', 'right_slow', 'right_fast']
            for force in force_terms:
                forces[force] = 0
            forces['stop'] = max(min(pa['up'], pv['stop']), min(pa['up_right'], pv['ccw_slow']),min(pa['up_left'], pv['cw_slow']))

            forces['right_fast'] = max(min(pa['up_more_right'], pv['ccw_slow']), forces['right_fast'])
            forces['right_fast'] = max(min(pa['up_more_right'], pv['cw_slow']), forces['right_fast'])

            forces['left_fast'] = max(min(pa['up_more_left'], pv['ccw_slow']), forces['left_fast'])
            forces['left_fast'] = max(min(pa['up_more_left'], pv['cw_slow']), forces['left_fast'])

            forces['left_slow'] = max(min(pa['up_more_right'], pv['ccw_fast']), forces['left_slow'])
            forces['right_fast'] = max(min(pa['up_more_right'], pv['cw_fast']), forces['right_fast'])

            forces['right_slow'] = max(min(pa['up_more_left'], pv['cw_fast']), forces['right_slow'])
            forces['left_fast'] = max(min(pa['up_more_left'], pv['ccw_fast']), forces['left_fast'])

            forces['right_fast'] = max(min(pa['down_more_right'], pv['ccw_slow']), forces['right_fast'])
            forces['stop'] = max(min(pa['down_more_right'], pv['cw_slow']), forces['stop'])

            forces['left_fast'] = max(min(pa['down_more_left'], pv['cw_slow']), forces['left_fast'])
            forces['stop'] = max(min(pa['down_more_left'], pv['ccw_slow']), forces['stop'])
            #13 14
            forces['stop'] = max(min(pa['down_more_right'], pv['ccw_fast']), forces['stop'])
            forces['stop'] = max(min(pa['down_more_right'], pv['cw_fast']), forces['stop'])

            forces['stop'] = max(min(pa['down_more_left'], pv['cw_fast']), forces['stop'])
            forces['stop'] = max(min(pa['down_more_left'], pv['ccw_fast']), forces['stop'])
            #17, 18
            forces['right_fast'] = max(min(pa['down_right'], pv['cw_slow']), forces['right_fast'])
            forces['right_fast'] = max(min(pa['down_right'], pv['ccw_slow']), forces['right_fast'])

            forces['left_fast'] = max(min(pa['down_left'], pv['cw_slow']), forces['left_fast'])
            forces['left_fast'] = max(min(pa['down_left'], pv['ccw_slow']), forces['left_fast'])
            #21, 22
            forces['stop'] = max(min(pa['down_right'], pv['ccw_fast']), forces['stop'])
            forces['right_slow'] = max(min(pa['down_right'], pv['cw_fast']), forces['right_slow'])

            forces['stop'] = max(min(pa['down_left'], pv['cw_fast']), forces['stop'])
            forces['left_slow'] = max(min(pa['down_left'], pv['ccw_fast']), forces['left_slow'])

            forces['right_slow'] = max(min(pa['up_right'], pv['ccw_slow']), forces['right_slow'])
            forces['right_fast'] = max(min(pa['up_right'], pv['cw_slow']), forces['right_fast'])
            #27, 28
            forces['right_fast'] = max(min(pa['up_right'], pv['stop']), forces['right_fast'])
            forces['left_slow'] = max(min(pa['up_left'], pv['cw_slow']), forces['left_slow'])

            forces['left_fast'] = max(min(pa['up_left'], pv['ccw_slow']), forces['left_fast'])
            forces['left_fast'] = max(min(pa['up_left'], pv['stop']), forces['left_fast'])

            forces['left_fast'] = max(min(pa['up_right'], pv['ccw_fast']), forces['left_fast'])
            forces['right_fast'] = max(min(pa['up_right'], pv['cw_fast']), forces['right_fast'])
            #33, 34
            forces['right_fast'] = max(min(pa['up_left'], pv['cw_fast']), forces['right_fast'])
            forces['left_fast'] = max(min(pa['up_left'], pv['ccw_fast']), forces['left_fast'])

            forces['right_fast'] = max(min(pa['down'], pv['stop']), forces['right_fast'])
            forces['stop'] = max(min(pa['down'], pv['cw_fast']), forces['stop'])

            forces['stop'] = max(min(pa['down'], pv['ccw_fast']), forces['stop'])
            forces['left_slow'] = max(min(pa['up'], pv['ccw_slow']), forces['left_slow'])
            #39,40
            forces['left_fast'] = max(min(pa['up'], pv['ccw_fast']), forces['left_fast'])
            forces['right_slow'] = max(min(pa['up'], pv['cw_slow']), forces['right_slow'])

            forces['right_fast'] = max(min(pa['up'], pv['cw_fast']), forces['right_fast'])
            forces['stop'] = max(min(pa['up'], pv['stop']), forces['stop'])

            #Bonus rules
            forces['right_fast'] = max(min(cp['left_far'], cv['left_fast']), forces['right_fast'])
            forces['right_fast'] = max(min(cp['left_near'], cv['left_fast']), forces['right_fast'])

            forces['right_slow'] = max(min(cp['left_near'], cv['left_fast']), forces['right_slow'])
            forces['stop'] = max(min(cp['stop'], cv['stop']), forces['stop'])

            forces['left_slow'] = max(min(cp['right_near'], cv['right_fast']), forces['left_slow'])
            forces['left_fast'] = max(min(cp['right_near'], cv['right_fast']), forces['left_fast'])

            forces['left_fast'] = max(min(cp['right_far'], cv['right_fast']), forces['left_fast'])

            return forces


    class BonusRules:
        def __init__(self):
            pass

        def infer(self, input):
            pa = input['pa']
            pv = input['pv']
            forces = {}
            force_terms = ['left_fast', 'left_slow', 'stop', 'right_slow', 'right_fast']
            for force in force_terms:
                forces[force] = 0
            forces['stop'] = max(min(pa['up'], pv['stop']), min(pa['up_right'], pv['ccw_slow']),
                                 min(pa['up_left'], pv['cw_slow']))

            forces['right_fast'] = max(min(pa['up_more_right'], pv['ccw_slow']), forces['right_fast'])


