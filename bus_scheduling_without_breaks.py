from ortools.sat.python import cp_model
from math import ceil

shifts = [
    [0, '07:00', '07:30', 420, 450, 30],
    [1, '07:30', '08:00', 450, 480, 30],
    [2, '08:00', '08:30', 480, 510, 30],
    [3, '08:30', '09:00', 510, 540, 30],
    [4, '09:00', '09:30', 540, 570, 30],
    [5, '09:30', '10:00', 570, 600, 30],
    [6, '10:00', '10:30', 600, 630, 30],
    [7, '10:30', '11:00', 630, 660, 30],
    [8, '11:00', '11:30', 660, 690, 30],
    [9, '11:30', '12:00', 690, 720, 30],
    [10, '12:00', '12:30', 720, 750, 30],
    [11, '12:30', '13:00', 750, 780, 30],
    [12, '13:00', '13:30', 780, 810, 30],
    [13, '13:30', '14:00', 810, 840, 30],
    [14, '14:00', '14:30', 840, 870, 30],
    [15, '14:30', '15:00', 870, 900, 30],
    [16, '15:00', '15:30', 900, 930, 30],
    [17, '15:30', '16:00', 930, 960, 30],
    [18, '16:00', '16:30', 960, 990, 30],
    [19, '16:30', '17:00', 990, 1020, 30],
    [20, '17:00', '17:30', 1020, 1050, 30],
    [21, '17:30', '18:00', 1050, 1080, 30],
    [22, '18:00', '18:30', 1080, 1110, 30],
    [23, '18:30', '19:00', 1110, 1140, 30],
    [24, '19:00', '19:30', 1140, 1170, 30],
    [25, '19:30', '20:00', 1170, 1200, 30],
    [26, '20:00', '20:30', 1200, 1230, 30],
    [27, '20:30', '21:00', 1230, 1260, 30],
    [28, '21:00', '21:30', 1260, 1290, 30],
    [29, '21:30', '22:00', 1290, 1320, 30],
    [30, '22:00', '22:30', 1320, 1350, 30],
    [31, '22:30', '23:00', 1350, 1380, 30],
    [32, '23:00', '23:30', 1380, 1410, 30],
    [33, '23:30', '24:00', 1410, 1440, 30]
]

class VarArraySolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(self, driver_shifts, num_drivers, num_shifts, solutions):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.driver_shifts = driver_shifts
        self.num_drivers = num_drivers
        self.num_shifts = num_shifts
        self.solutions = solutions
        self.solution_id = 0

    def on_solution_callback(self):
        if self.solution_id in self.solutions:
            self.solution_id += 1
            print ("Solution found!")
            for driver_id in range(self.num_drivers):
                print ("*************Driver#%s*************" % driver_id)
                for shift_id in range(self.num_shifts):
                    if (self.Value(self.driver_shifts[(driver_id, shift_id)])):
                        print('Shift from %s to %s' %
                              (shifts[shift_id][1],
                               shifts[shift_id][2]))
            print()

    def solution_count(self):
        return self.solution_id

solver = cp_model.CpSolver()
model = cp_model.CpModel()

num_shifts = len(shifts)
working_time = 24
latest_start_shift = num_shifts - working_time
num_drivers = ceil(float(num_shifts) / working_time)

# create an array of assignments of drivers
driver_shifts = {}
for driver_id in range(num_drivers):
    for shift_id in range(num_shifts):
        driver_shifts[(driver_id, shift_id)] = model.NewBoolVar('driver%ishift%i' % (driver_id, shift_id))

# driver must work exactly {working_time} shifts
for driver_id in range(num_drivers):
    model.Add(sum(driver_shifts[(driver_id, shift_id)] for shift_id in range(num_shifts)) == working_time)

# each shift must be covered by at least one driver
for shift_id in range(num_shifts):
    model.Add(sum(driver_shifts[(driver_id, shift_id)] for driver_id in range(num_drivers)) >= 1)

# create an array of start times for drivers
start_time = {}
for driver_id in range(num_drivers):
    for shift_id in range(latest_start_shift + 1):
        start_time[(driver_id, shift_id)] = model.NewBoolVar('driver%istart%i' % (driver_id, shift_id))

#
for driver_id in range(num_drivers):
     for start_shift_id in range(latest_start_shift + 1):
         model.Add(sum(driver_shifts[(driver_id, shift_id)] for shift_id in range(start_shift_id, start_shift_id + working_time)) == working_time)\
             .OnlyEnforceIf(start_time[(driver_id, start_shift_id)])

for driver_id in range(num_drivers):
    model.Add(sum(start_time[(driver_id, start_shift_id)] for start_shift_id in range(latest_start_shift + 1)) == 1)

solution_printer = VarArraySolutionPrinter(driver_shifts, num_drivers, num_shifts, range(2))
status = solver.SearchForAllSolutions(model, solution_printer)
