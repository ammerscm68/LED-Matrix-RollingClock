from gpiozero import CPUTemperature
cpu = CPUTemperature()
print(cpu.temperature)

def cpu_temp():
    sensor_file = '/sys/class/thermal/thermal_zone0/temp'

    with io.open(sensor_file, 'r') as f:
        return float(f.readline().strip()) / 1000

print(cpu_temp())



