import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import networkx as nx
import math
import itertools
from matplotlib.widgets import Button

def check_state_possible(phase_string: str):
  assert len(phase_string) == 12
  ANS, AEW, ASN, AWE, RSE, REN, RNW, RWS, LSW, LES, LNE, LWN = map(lambda c: True if c == 'G' else False, phase_string)
  mANS, mAEW, mASN, mAWE, mRSE, mREN, mRNW, mRWS, mLSW, mLES, mLNE, mLWN = map(lambda c: True if c == 'g' else False, phase_string)

  if (ANS and AEW or ANS and AWE or ASN and AEW or ASN and AWE):
    # conflicing aheads
    return False

  if (LSW and LES or LES and LNE or LNE and LWN or LWN and LSW):
    # conflicting lefts
    return False

  if (LSW and AWE or LWN and ANS or LNE and AEW or LES and ASN):
    # conflicing aheads and lefts
    return False

  if (LNE and ASN or LES and AWE or LSW and ANS or LWN and AEW):
    # conflicing lefts with opposite direction aheads
    return False

  if (ANS + RNW == 1 or AEW + REN == 1 or ASN + RSE == 1 or AWE + RWS == 1):
    # right turn and ahead phase need to be the same because they share a lane
    return False

  if (ANS + RWS + LES > 1 or AEW + RNW + LSW > 1 or ASN + REN + LWN > 1 or AWE + RSE + LNE > 1):
    # multiple 'G's on one arrival lane
    return False

  # MINOR GREENS
  if (mANS or mAEW or mASN or mAWE):
    # I have only seen minor aheads for cycles
    return False
  
  if (mLNE and not ASN or mLES and not AWE or mLSW and not ANS or mLWN and not AEW):
    # If there is no oncoming green, then lefts should be major green
    return False

  if (mRNW and not ANS or mREN and not AEW or mRSE and not ASN or mRWS and not AWE):
    # right turn and ahead phase need to be green at the same time because they share a lane.
    return False

  if (mLNE and not ANS or mLES and not AEW or mLSW and not ASN or mLWN and not AWE):
    # The left cannot be minor if the major ahead is not active, this is because 
    # minor lefts happen when the signal is a standard green (vs an arrow)
    return False 

  return True

class stateViewer:
  def __init__(self, combinations, isValid, G, pos, colourMap, rows, cols):
    self.combinations = combinations
    self.isValid = isValid
    self.G = G
    self.pos = pos
    self.colourMap = colourMap
    self.rows = rows
    self.cols = cols
    self.perPage = rows * cols
    self.currentPage = 0

    self.fig = plt.figure(figsize=(16, 9))
    self._setup_buttons()
    self.draw_page(0)

  def nextPage(self, event):
    if (self.currentPage + 1) * self.perPage < len(self.combinations):
      self.currentPage += 1
      self.draw_page(self.currentPage)

  def prevPage(self, event):
    if self.currentPage > 0:
      self.currentPage -= 1
      self.draw_page(self.currentPage)

  def _setup_buttons(self):
    self.axnext = plt.axes([0.55, 0.03, 0.1, 0.05])
    self.axprev = plt.axes([0.35, 0.03, 0.1, 0.05])

    self.bnext = Button(self.axnext, 'Next')
    self.bprev = Button(self.axprev, 'Previous')
    self.bnext.on_clicked(self.nextPage)
    self.bprev.on_clicked(self.prevPage)

  def _draw_phase(self, phase_string, ax):
    colours = [self.colourMap[c] for c in phase_string]

    # print(pos)
    nx.draw_networkx_nodes(self.G, self.pos, ax=ax, node_size=20, node_color='lightgray')
    nx.draw_networkx_labels(self.G, self.pos, ax=ax, font_size=8)
    nx.draw_networkx_edges(self.G, self.pos, edgelist=aheadEdges, edge_color=colours[:len(aheadEdges)], width=2, arrows=True, ax=ax)
    nx.draw_networkx_edges(self.G, self.pos, edgelist=rightEdges, edge_color=colours[len(aheadEdges):len(aheadEdges) + len(rightEdges)], connectionstyle=f'arc3,rad=-0.4', width=2, arrows=True, ax=ax)
    nx.draw_networkx_edges(self.G, self.pos, edgelist=leftEdges, edge_color=colours[-len(leftEdges):], connectionstyle=f'arc3,rad=0.4', width=2, arrows=True, ax=ax)

    return

  def draw_page(self, page):
    gs = gridspec.GridSpec(self.rows, self.cols, figure=self.fig)
    start = page * self.perPage
    end = min(start + self.perPage, len(self.combinations))

    # Remove old plot axes (axes that are used for previous page)
    for ax in [a for a in self.fig.get_axes() if a.get_title() != '']:
      ax.remove()

    for i, idx in enumerate(range(start, end)):
      thisState = self.combinations[idx]

      ax = self.fig.add_subplot(gs[i]) 
      ax.set_axis_off()

      self._draw_phase(thisState[1], ax)

      ax.set_title(f"#{thisState[0]}: {thisState[1]}")
      ax.title.set_fontsize(8)
      if (check_state_possible(thisState[1])):
        ax.title.set_color('green')
      else:
        ax.title.set_color('red')
    
    self.fig.suptitle(f"Page {page + 1} / {len(self.combinations) // self.perPage + 1}\nTotal {len(self.combinations)} {'valid' if self.isValid else 'invalid'} combinations")
    self.fig.subplots_adjust(bottom=0.15)
    self.fig.canvas.draw_idle()

colourMap = {
  'r': 'red',
  # 'y': 'yellow',
  'g': 'green',
  'G': 'lime'
}

combinations = list(map(''.join, itertools.product(colourMap.keys(), repeat=12)))

validCombinations: list[tuple[int, str]] = []
invalidCombinations: list[tuple[int, str]] = []

for i in range(len(combinations)):
  if check_state_possible(combinations[i]):
    validCombinations.append((i, combinations[i]))
  else:
    invalidCombinations.append((i, combinations[i]))

print(f"Total {len(combinations)} combinations, of which {len(validCombinations)} valid ({100 * len(validCombinations) / len(combinations)} %)")

# Generate the intersection shape
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

commonKwargs = {'G': G, 'pos': pos, 'colourMap': colourMap, 'rows': 5, 'cols': 10}

validViewer = stateViewer(combinations=validCombinations, isValid=True, **commonKwargs)
invalidViewer = stateViewer(combinations=invalidCombinations, isValid=False, **commonKwargs)

plt.show()