import numpy as np
from matplotlib import pyplot as plt

f = open('arena_results.txt')
lines = f.readlines()

print('AlphaZero vs MCTS')

x_values = np.array([])
y_values = np.array([])

for index, line in enumerate(lines):
    words = line.split()
    win_rate = int(round(float(words[7][:4]), 0))

    x_values = np.append(x_values, index)
    y_values = np.append(y_values, win_rate)


plt.plot(x_values, y_values)
plt.title('Procentaj victorii AlphaGo Zero vs MCTS')
plt.xlabel('Număr model')
plt.ylabel('Procentaj')
# plt.xlim(1, 41)
plt.ylim(0, 101)
plt.show()

f.close()

x_values = np.array([])
y_values = np.array([])

f = open('loss.txt')
lines = f.readlines()
skip = 0
for index, line in enumerate(lines):
    words = line.split()
    if words[0] != 'Iteratie:':
        x_values = np.append(x_values, index- skip)
        y_values = np.append(y_values, round(float(words[2][7:-1]), 3))
    else:
        skip += 1
f.close()

plt.xlabel('Epocă')
plt.ylabel('Cost')
plt.title('Evoluție cost')

colors = ['blue', 'black']
segment_length = 10

for i in range(segment_length, len(x_values), segment_length):
    # plt.plot(x_values[i-segment_length:i], y_values[i-segment_length:i], color=colors[i//segment_length % len(colors)])
    plt.plot(x_values[i - segment_length:i], y_values[i - segment_length:i], color = 'tab:blue')


# plt.ylim(0, 1000)
# plt.yticks(np.arange(0,0.5, 5))
# plt.xlim(0, 450)

plt.show()



f = open("model_iteration_progress.txt")
lines = f.readlines()

x_values = np.array([])
y_values = np.array([])

for index, line in enumerate(lines):
    words = line.split()
    win_rate = int(float(line.split()[9]) * 100)
    x_values = np.append(x_values, index + 1)
    y_values = np.append(y_values, win_rate)

plt.title('Procent victorii iterație nouă vs iterație veche')
plt.xlabel('Număr iterație nouă')
plt.ylabel('Procent')
# plt.xlim(1, 41)
plt.ylim(0, 101)
plt.plot(x_values, y_values)

# Calculate the linear regression coefficients
coefficients = np.polyfit(x_values, y_values, 1)
slope = coefficients[0]
intercept = coefficients[1]

# Generate x values for the trend line
x_trend = np.linspace(min(x_values), max(x_values), 100)

y_trend = slope * x_trend + intercept
plt.plot(x_trend, y_trend, color='red', label='Trend Line')

plt.show()

f.close()


