from matplotlib import colors
from numpy import array
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('data/TwoPointDistance.csv', usecols=['start_name', 'end_name', 'smooth_time_value(min)'])

all_link = [i for i in df['smooth_time_value(min)'].values if i != 0]

link_120 = [i for i in all_link if i<120]
link_90 = [i for i in all_link if i<90]
link_60 = [i for i in all_link if i<60]

plt.clf()
bplot = plt.boxplot([all_link, link_120, link_90, link_60], patch_artist=True)
plt.ylabel('Smooth travel time(min)')
plt.xlabel('Different time limits(min)')
plt.xticks([1, 2, 3, 4], [
    'no({})'.format(len(all_link)), 
    '<120({})'.format(len(link_120)), 
    '<90({})'.format(len(link_90)),
    '<60({})'.format(len(link_60))])

for patch in bplot['boxes']:
    patch.set_facecolor('lightcyan')

# plt.show()
plt.savefig('output/report/link_smooth_time_value_boxplot(full).png')
