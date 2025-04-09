import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import networkx as nx
import math
import itertools
from matplotlib.widgets import Button

colour_map = {
  'r': 'red',
  # 'g': 'green',
  'G': 'lime',
  # 'y': 'yellow'
}

combinations = list(map(''.join, itertools.product(colour_map.keys(), repeat=12)))

# Settings
per_page = 50
rows, cols = 5, 10
current_page = [0]  # Mutable for closure access


G = nx.DiGraph()

intersectionArmPositions = {'N': (0, 1), 'E': (1, 0), 'S': (0, -1), 'W': (-1, 0)}
intersectionArmAngles = {'N': 180, 'E': 270, 'S': 0, 'W': 90}
intersectionArmLanes = {'N': (2, 1), 'E': (2, 1), 'S': (2, 1), 'W': (2, 1)}

pos = {}

for (armName, armBasePos) in intersectionArmPositions.items():
  armAngle = intersectionArmAngles.get(armName)
  armLanes = intersectionArmLanes.get(armName)

  laneSpread = 0.75

  if (armAngle is not None and armLanes is not None):
    numberLanes = armLanes[0] + armLanes[1]
    laneStep = laneSpread / (numberLanes - 1)
    for i in range(numberLanes):
      # + / - are to get Lane 0 be right most in driving direction
      node_x = armBasePos[0] - math.cos(intersectionArmAngles[armName] * math.pi/180) * (i * laneStep - laneSpread / 2)
      node_y = armBasePos[1] + math.sin(intersectionArmAngles[armName] * math.pi/180) * (i * laneStep - laneSpread / 2)

      pos[armName + str(i)] = (round(node_x, 5), round(node_y, 1))

  G.add_nodes_from(pos.keys())
  aheadEdges = [('N0', 'S2'), ('E0', 'W2'), ('S0', 'N2'), ('W0', 'E2')]
  rightEdges = [('S0', 'E2'), ('E0', 'N2'), ('N0', 'W2'), ('W0', 'S2')]
  leftEdges = [('S1', 'W2'), ('E1', 'S2'), ('N1', 'E2'), ('W1', 'N2')]


def draw_phase(phase_string, ax):
  colours = [colour_map[c] for c in phase_string]

  # print(pos)
  nx.draw_networkx_nodes(G, pos, ax=ax, node_size=20, node_color='lightgray')
  nx.draw_networkx_labels(G, pos, ax=ax, font_size=8)
  nx.draw_networkx_edges(G, pos, edgelist=aheadEdges, edge_color=colours[:len(aheadEdges)], width=2, arrows=True, ax=ax)
  nx.draw_networkx_edges(G, pos, edgelist=rightEdges, edge_color=colours[len(aheadEdges):len(aheadEdges) + len(rightEdges)], connectionstyle=f'arc3,rad=-0.4', width=2, arrows=True, ax=ax)
  nx.draw_networkx_edges(G, pos, edgelist=leftEdges, edge_color=colours[-len(leftEdges):], connectionstyle=f'arc3,rad=0.4', width=2, arrows=True, ax=ax)

  return


def draw_page(page):
  # fig.clf()
  gs = gridspec.GridSpec(rows, cols, figure=fig)
  start = page * per_page
  end = min(start + per_page, len(combinations))

  # Remove old plot axes (axes that are used for previous page)
  for ax in [a for a in fig.get_axes() if a.get_title() != '']:
    ax.remove()

  for i, idx in enumerate(range(start, end)):
    thisState = combinations[idx]

    ax = fig.add_subplot(gs[i])
    ax.set_axis_off()

    draw_phase(thisState, ax)

    ax.set_title(f"#{idx}: {thisState}")
    ax.title.set_fontsize(10)
  
  fig.suptitle(f"Page {page + 1} / {len(combinations) // per_page}\nTotal {len(combinations)} combinations")
  fig.subplots_adjust(bottom=0.15)
  fig.canvas.draw_idle()


# Button callbacks
def next_page(event):
  if (current_page[0] + 1) * per_page < len(combinations):
    current_page[0] += 1
    draw_page(current_page[0])

def prev_page(event):
  if current_page[0] > 0:
    current_page[0] -= 1
    draw_page(current_page[0])

def redraw_buttons():
  # Add Buttons (they get re-created each time the page is drawn)
  axnext = plt.axes([0.55, 0.03, 0.1, 0.05])
  axprev = plt.axes([0.35, 0.03, 0.1, 0.05])

  bnext = Button(axnext, 'Next')
  bprev = Button(axprev, 'Previous')
  bnext.on_clicked(next_page)
  bprev.on_clicked(prev_page)

# Create initial figure
fig = plt.figure(figsize=(16, 9))
draw_page(0)
axnext = plt.axes([0.55, 0.03, 0.1, 0.05])
axprev = plt.axes([0.35, 0.03, 0.1, 0.05])

bnext = Button(axnext, 'Next')
bprev = Button(axprev, 'Previous')
bnext.on_clicked(next_page)
bprev.on_clicked(prev_page)

plt.show()