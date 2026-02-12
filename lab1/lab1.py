import random

random.seed(67)
random_enabled = False

def Random():
    if(random_enabled):
        return random.random()
    return 0

class RetailModel:
    def __init__(self, loan_available,
                 loan_interest,
                 purchase_price,
                 selling_price,
                 delivery_amount,
                 delivery_time,
                 retail_time,
                 part_pay_loan):
        self.month = 0
        self.funds = 0
        self.loan = 0
        self.loan_available = loan_available * 1000

        self.purchase_price = purchase_price
        self.selling_price = selling_price
        self.delivery_time = delivery_time
        self.retail_time = retail_time

        self.delivery_list = []
        self.retail_list = []

        self.loan_interest = loan_interest / 100 / 12 + 1
        self.delivery_amount = delivery_amount * 1000
        self.customs_duty = 0.3

        self.part_pay_loan = part_pay_loan

    def __repr__(self) -> str:
        return (f"{self.month}; "
                f"{self.funds}; "
                f"{self.loan}; "
                f"{self.loan_available}"
                f"; {self.delivery_list}"
                f"; {self.retail_list}"
                "\n"
                )

    def getHeader() -> str:
        return ("month; "
                "funds; "
                "loan; "
                "loan_available"
                "; delivery_list"
                "; retail_list"
                "\n"
                )
    
    def pay(self, amount, type) -> bool:
        if(type == "start"):
            fee = len(self.delivery_list) + 1
        elif(type == "finish"):
            fee = len(self.delivery_list) - 1
        else:
            raise ValueError("Wrong type.")
        fee *= (self.customs_duty *
                self.delivery_amount *
                self.purchase_price)
        
        if(self.funds + self.loan_available
           < amount + fee):
            return False
        if(self.funds - amount > 0):
            self.funds -= amount
            return True
        amount -= self.funds
        self.funds = 0
        self.loan += amount
        self.loan_available -= amount
        return True

    def startDelivery(self):
        if(self.pay((1 - self.customs_duty) * 
                    self.purchase_price *
                    self.delivery_amount,
                    "start")):
            self.delivery_list.append(self.month +
                                      self.delivery_time)

    def startRetail(self):
        num = Random()
        if(num <= 0.5):
            num = 0
        elif(num <= 0.7):
            num = 1
        elif(num <= 0.9):
            num = 2
        else:
            num = 3
        self.retail_list.append(self.month +
                                self.retail_time +
                                num)

    def finishDelivery(self):
        while(len(self.delivery_list) != 0 and
              self.delivery_list[0] == self.month):
            if(not self.pay(self.customs_duty * 
                            self.purchase_price *
                            self.delivery_amount,
                            "finish")):
                raise ValueError("CANNOT PAY CUSTOM DUTY!")
            self.startRetail()
            self.delivery_list.pop(0)

    def finishRetail(self):
        for i in range(len(self.retail_list) - 1, -1, -1):
            if(self.retail_list[i] == self.month):
                money_received = (self.selling_price *
                                  self.delivery_amount)
                if(self.loan < money_received * self.part_pay_loan):
                    money_received -= self.loan
                    self.loan = 0
                    self.funds += money_received
                else:
                    self.loan -= money_received * self.part_pay_loan
                    self.funds += money_received * (1 - self.part_pay_loan)
                self.retail_list.pop(i)


        while(len(self.retail_list) != 0 and
              self.retail_list[0] == self.month):
                money_received = (self.selling_price *
                                self.delivery_amount)
                if(self.loan < money_received * self.part_pay_loan):
                    money_received -= self.loan
                    self.loan = 0
                    self.funds += money_received
                else:
                    self.loan -= money_received * self.part_pay_loan
                    self.funds += money_received * (1 - self.part_pay_loan)
                self.retail_list.pop(0)

    def monthElapsed(self):
        self.loan *= self.loan_interest
        self.finishRetail()
        self.finishDelivery()
        self.startDelivery()
        self.month += 1

    def setPurchasePrice(self, value):
        self.purchase_price = value

    def setSellingPrice(self, value):
        self.selling_price = value

    def setDeliveryTime(self, value):
        self.delivery_time = value

    def setRetailTime(self, value):
        self.retail_time = value

# lab 1 part 1

file = open("lab1_1_expected_part_pay_loan.csv", 'w')
file.write("part_pay_loan; profit; loan\n")
best_part_pay_loan = 0
best_profit = 0
for i in range(0, 101, 1):
    model = RetailModel(
    loan_available = 7000,
    loan_interest = 13,
    purchase_price = 170,
    selling_price = 260,
    delivery_amount = 12,
    delivery_time = 2,
    retail_time = 2,
    part_pay_loan = i / 100)
    for j in range(0, 20, 1):
        model.monthElapsed()
    file.write(f"{i}; {model.funds - model.loan}; {7000000 - model.loan_available}\n")
    if(model.funds - model.loan > best_profit):
        best_profit = model.funds - model.loan
        best_part_pay_loan = i
print(best_part_pay_loan)
file.close()

model = RetailModel(
    loan_available = 7000,
    loan_interest = 13,
    purchase_price = 170,
    selling_price = 260,
    delivery_amount = 12,
    delivery_time = 2,
    retail_time = 2,
    part_pay_loan = best_part_pay_loan / 100)
file = open("lab1_1_expected_opt.csv", 'w')
file.write(RetailModel.getHeader())
file.write(repr(model))
for i in range(0, 60, 1):
    model.monthElapsed()
    file.write(repr(model))
file.close()

# lab 1 part 2

model = RetailModel(
    loan_available = 7000,
    loan_interest = 13,
    purchase_price = 170,
    selling_price = 260,
    delivery_amount = 12,
    delivery_time = 2,
    retail_time = 2,
    part_pay_loan = best_part_pay_loan / 100)
file = open("lab1_2_real.csv", 'w')
file.write(RetailModel.getHeader())
file.write(repr(model))
for i in range(0, 60, 1):
    if(i == 3):
        model.setRetailTime(3)
        model.setSellingPrice(220)
    model.monthElapsed()
    file.write(repr(model))
file.close()

file = open("lab1_2_real_part_pay_loan.csv", 'w')
file.write("part_pay_loan; profit; loan\n")
best_part_pay_loan = 0
best_profit = 0
for i in range(0, 101, 1):
    model = RetailModel(
        loan_available = 7000,
        loan_interest = 13,
        purchase_price = 170,
        selling_price = 260,
        delivery_amount = 12,
        delivery_time = 2,
        retail_time = 2,
        part_pay_loan = i / 100)
    for j in range(0, 50, 1):
        if(j == 3):
            model.setRetailTime(3)
            model.setSellingPrice(220)
        model.monthElapsed()
    file.write(f"{i}; {model.funds - model.loan}; {7000000 - model.loan_available}\n")
    if(model.funds - model.loan > best_profit):
        best_profit = model.funds - model.loan
        best_part_pay_loan = i
print(best_part_pay_loan)
file.close()

model = RetailModel(
    loan_available = 7000,
    loan_interest = 13,
    purchase_price = 170,
    selling_price = 260,
    delivery_amount = 12,
    delivery_time = 2,
    retail_time = 2,
    part_pay_loan = best_part_pay_loan / 100)
file = open("lab1_2_real_opt.csv", 'w')
file.write(RetailModel.getHeader())
file.write(repr(model))
for i in range(0, 60, 1):
    if(i == 3):
        model.setRetailTime(3)
        model.setSellingPrice(220)
    model.monthElapsed()
    file.write(repr(model))
file.close()

# lab 1 part 3

random_enabled = True

random.seed(67)
model = RetailModel(
    loan_available = 7000,
    loan_interest = 13,
    purchase_price = 170,
    selling_price = 260,
    delivery_amount = 12,
    delivery_time = 2,
    retail_time = 2,
    part_pay_loan = best_part_pay_loan / 100)
file = open("lab1_3_real_random.csv", 'w')
file.write(RetailModel.getHeader())
file.write(repr(model))
for i in range(0, 60, 1):
    if(i == 3):
        model.setRetailTime(3)
        model.setSellingPrice(220)
    model.monthElapsed()
    file.write(repr(model))
file.close()

file = open("lab1_3_real_random_part_pay_loan.csv", 'w')
file.write("part_pay_loan; profit; loan\n")
best_part_pay_loan = 0
best_profit = 0
for i in range(0, 101, 1):
    random.seed(67)
    model = RetailModel(
        loan_available = 7000,
        loan_interest = 13,
        purchase_price = 170,
        selling_price = 260,
        delivery_amount = 12,
        delivery_time = 2,
        retail_time = 2,
        part_pay_loan = i / 100)
    for j in range(0, 60, 1):
        if(j == 3):
            model.setRetailTime(3)
            model.setSellingPrice(220)
        model.monthElapsed()
    file.write(f"{i}; {model.funds - model.loan}; {7000000 - model.loan_available}\n")
    if(model.funds - model.loan > best_profit):
        best_profit = model.funds - model.loan
        best_part_pay_loan = i
print(best_part_pay_loan)
file.close()

random.seed(67)
model = RetailModel(
    loan_available = 7000,
    loan_interest = 13,
    purchase_price = 170,
    selling_price = 260,
    delivery_amount = 12,
    delivery_time = 2,
    retail_time = 2,
    part_pay_loan = best_part_pay_loan / 100)
file = open("lab1_3_real_random_opt.csv", 'w')
file.write(RetailModel.getHeader())
file.write(repr(model))
for i in range(0, 60, 1):
    if(i == 3):
        model.setRetailTime(3)
        model.setSellingPrice(220)
    model.monthElapsed()
    file.write(repr(model))
file.close()
