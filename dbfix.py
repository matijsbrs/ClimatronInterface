import mysql.connector

mydb = mysql.connector.connect(
  host="192.168.2.201",
  user="broker",
  password="nopassword",
  database="datastore"
)

print(mydb)

mycursor = mydb.cursor()

mycursor.execute("SELECT * FROM EnergyCounters WHERE TimeStamp between NOW() - INTERVAL 1 MONTH and now()")

preload = 1
prevWhUsage = 0
prevWhProduction = 0
prevGasUsage=0
prevHeatingUsage=0
prevTimeStamp = 0
preprevWhUsage = 0
preprevWhProduction = 0
preprevGasUsage=0
preprevHeatingUsage=0
preprevTimeStamp = 0
for (TimeStamp, WhUsage, WhProduction, GasUsage, HeatingUsage) in mycursor:
    if preload:
        preload = 0
        prevWhUsage = WhUsage
        prevWhProduction = WhProduction
        prevGasUsage= GasUsage
        prevHeatingUsage= HeatingUsage
        prevTimeStamp = TimeStamp
        preprevWhUsage = WhUsage
        preprevWhProduction = WhProduction
        preprevGasUsage= GasUsage
        preprevHeatingUsage= HeatingUsage
        preprevTimeStamp = TimeStamp
    else:
        if ( prevWhUsage > WhUsage ) or (prevWhProduction > WhProduction) or (prevGasUsage > GasUsage) or (prevHeatingUsage > HeatingUsage):
          # print("{} {} {} {} {}".format(TimeStamp, WhUsage, WhProduction, GasUsage, HeatingUsage))
          if prevWhUsage > WhUsage: 
            cause = "WhUsage"
            update = "delete from EnergyCounters where TimeStamp = '{}';".format(TimeStamp)
          if prevWhProduction > WhProduction: 
            cause = "WhProduction"
            update = "delete from EnergyCounters where TimeStamp = '{}';".format(TimeStamp)
          if prevGasUsage > GasUsage: 
            cause = "GasUsage"
            update = "delete from EnergyCounters where TimeStamp = '{}';".format(TimeStamp)
          if prevHeatingUsage > HeatingUsage: 
            cause = "HeatinUsage"
            update = "delete from EnergyCounters where TimeStamp = '{}';".format(TimeStamp)

          #print("{} - {} {} {} {} {}".format(cause, prevTimeStamp, prevWhUsage, prevWhProduction, prevGasUsage, prevHeatingUsage))
          print(update)
          # print()

        preprevWhUsage = prevWhUsage
        preprevWhProduction = prevWhProduction
        preprevGasUsage= prevGasUsage
        preprevHeatingUsage= prevHeatingUsage
        preprevTimeStamp = prevTimeStamp

        prevWhUsage = WhUsage
        prevWhProduction = WhProduction
        prevGasUsage= GasUsage
        prevHeatingUsage= HeatingUsage
        prevTimeStamp = TimeStamp
        




# myresult = mycursor.fetchall()

# for x in myresult:
#   print(x)