import numpy as np
import pandas as pd
from datetime import datetime
from csv import writer

from functools import partial

class Variable:
    def __init__(self, name, valueFns):
        self.name = name
        self.valueFns = valueFns

class Simulation:
    def __init__(self, vars):
        self.vars = vars
        self.varMap = {}
        self.initVars()

    def initVars(self):
        for v in self.vars:
            self.varMap[v.name] = v.valueFns

    def startSim(self, simFn, name):
        dt = datetime.today()
        self.out = writer(open(name + "-" + str(dt.timestamp()) + ".csv", 'a+',  newline='', encoding='utf-8'))

        header = list(self.varMap)
        header.insert(0, "year")
        header.append("total income")
        self.out.writerow(header)
        self.runSim(self.varMap, simFn, name)

    def runSim(self, vars, simFn, name):
        rec = False
        for var in vars:
            if isinstance(vars[var], list):
                rec = True
                for f in vars[var]:
                    cVars = vars.copy()
                    cVars[var] = f
                    self.runSim(cVars, simFn, name)
                break
        if not rec:
            print("new sim run")
            
            for yr in range(10):
                values = list(map(lambda v: str(vars[v](yr)), vars))
                values.insert(0, str(yr))
                values.append(str(simFn(vars, yr)))
                self.out.writerow(values)
                print(name + ", " + str(yr) + ", " + str(simFn(vars, yr)))

# Helper functions

def createSingleYear(y, value):
    return lambda yr: value if yr == y else 0

def createFixedIncrease(initial, inc):
    return lambda yr: initial + yr * inc

def createMultipleIncrease(initial, factor):
    return lambda yr: initial + initial * yr * factor

def createPowerIncrease(initial, power):
    return lambda yr: initial * pow(power, yr)

def createConstant(value):
    return lambda yr: value

def createFromList(list):
    return lambda yr: list[yr] 


# Sims

def publicBC(vars, yr):
    # fixed
    admin = vars["admin"](yr)
    legal = vars["legal"](yr)
    recruitment = vars["recruitment"](yr)
    thirdParty = vars["thirdparty"](yr)
    operating = vars["operating"](yr)

    # income
    payment = vars["access"](yr) * vars["dataaccess"](yr) * vars["dataconsumers"](yr)
    registration = vars["dataconsumers"](yr) * vars["license"](yr)

    # expediture
    registrationFees = vars["members"](yr) * vars["execution"](yr)/10 * vars["medium"](yr)
    queryCost = vars["dataconsumers"](yr) * vars["queries"](yr) * vars["execution"](yr)/10 * vars["high"](yr)
    dataPayment = vars["dataconsumers"](yr) * vars["dataaccess"](yr) * vars["execution"](yr)/10 * vars["medium"](yr)
    preferenceChange = vars["members"](yr) * vars["execution"](yr)/10
    distribution = vars["members"](yr) * vars["execution"](yr)/10 * vars["high"](yr)
    

    fixed = admin + legal + recruitment + thirdParty + operating
    income = payment + registration
    expenditure = registrationFees + queryCost + dataPayment + preferenceChange
    

    return income - fixed - expenditure

def ownBC(vars, yr):
    # fixed
    admin = vars["admin"](yr)
    legal = vars["legal"](yr)
    recruitment = vars["recruitment"](yr)
    thirdParty = vars["thirdparty"](yr)
    operating = vars["operating"](yr)

    # income
    registration = vars["dataconsumers"](yr) * vars["license"](yr)
    payment = vars["access"](yr) * vars["dataaccess"](yr) * vars["dataconsumers"](yr)
    registrationFees = vars["members"](yr) * vars["execution"](yr)/10 * vars["medium"](yr)
    queryCost = vars["dataconsumers"](yr) * vars["queries"](yr) * vars["execution"](yr)/10 * vars["high"](yr)
    dataPayment = vars["dataconsumers"](yr) * vars["dataaccess"](yr) * vars["execution"](yr)/10 * vars["medium"](yr)
    preferenceChange = vars["members"](yr) * vars["execution"](yr)/10

    # expenditure
    distribution = vars["members"](yr) * vars["execution"](yr)/10 * vars["high"](yr)    

    fixed = admin + legal + recruitment + thirdParty + operating
    income = payment + registration + registrationFees + queryCost + dataPayment
    expenditure = distribution

    return income - fixed - expenditure

def thirdPartyBC(vars, yr):
        # fixed
    admin = vars["admin"](yr)
    legal = vars["legal"](yr)
    recruitment = vars["recruitment"](yr)
    thirdParty = vars["thirdparty"](yr)
    operating = vars["operating"](yr)

    # income
    registration = vars["dataconsumers"](yr) * vars["license"](yr)
    payment = vars["access"](yr) * vars["dataaccess"](yr) * vars["dataconsumers"](yr)

    # expenditure
    distribution = vars["members"](yr) * vars["execution"](yr)/10 * vars["high"](yr)    

    fixed = admin + legal + recruitment + thirdParty + operating
    income = payment + registration
    expenditure = distribution

    return income - fixed - expenditure


def initSimVariables():
    # fixed costs
    admin = Variable("admin", createConstant(500000))
    legal = Variable("legal", createConstant(200000))
    recruitment = Variable("recruitment", createConstant(400000))
    operating = Variable("operating", createConstant(100000))
    thirdParty = Variable("thirdparty", createConstant(100000))

    # growth
    dataConsumers = Variable("dataconsumers", list(map(partial(createMultipleIncrease, 1), range(1, 5))))
    license = Variable("license", createConstant(10000))
    members = Variable("members", list(map(partial(createMultipleIncrease, 1000), range(1, 5))))
    high = Variable("high", createConstant(100))
    medium = Variable("medium", createConstant(10))
    low = Variable("low", createConstant(1))
    execution = Variable("execution", list(map(createConstant, range(1,11))))

    dataAccess = Variable("dataaccess", list(map(partial(createMultipleIncrease, 100), range(2, 5))))
    reward = Variable("reward", list(map(createConstant, range(1, 11))))
    queries = Variable("queries", list(map(partial(createMultipleIncrease, 8), range(1, 5))))
    access = Variable("access", list(map(createConstant, range(1, 8))))
    fees = Variable("fees", list(map(createConstant, range(1, 11))))
    
    return Simulation([admin, legal, recruitment, operating, thirdParty, dataConsumers, license, members, high, medium, low, execution, dataAccess, reward, queries, access, fees]) 

def runPublicBC():    
    sim = initSimVariables()
    sim.startSim(publicBC, "public_blockchain")

def runOwnBC():
    sim = initSimVariables()
    sim.startSim(ownBC, "own_blockchain")

def runThirdPartyBC():
    sim = initSimVariables()
    sim.startSim(thirdPartyBC, "third_party_blockchain")

# main


def main():
    runPublicBC()
    runOwnBC()
    runThirdPartyBC()


if __name__ == "__main__":
    main()


    

