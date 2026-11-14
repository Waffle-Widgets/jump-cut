"""Works out WHERE every city piece goes, and writes it to Art/Blender/export/City/city_layout.json.

    py tools/jumpcut_city_layout.py

Nothing in here touches Unreal or Blender. It is pure arithmetic over the level that already exists, so it
runs anywhere, in a second, and both consumers read the same file:
    tools/jumpcut_city_place.py        places it in Unreal          (GameStation / Justin's Mac - the builder)
    Art/Blender/jumpcut_city_kit.py    renders a mock-up of it       (any maker, to check it before anyone builds)

THE LEVEL IT IS FITTING, from tools/c1_layout.py (cm, Z up, floor top at z = 0, the route runs along +X):
    cafe       x  -630 ..   630,  y  -515 ..  515     12.6 x 10.3 m room, door in the EAST wall at x = 615
    street     x   630 ..  6600,  y  -500 ..  500     59.7 m long, 10 m wide
    plaza      x  6600 ..  9640,  y -1520 .. 1520     30 x 30 m, entry gate x = 6620, exit gate x = 9620
    exit run   x  9640 .. 10630,  y  -250 ..  250     Marker_Win at x = 10220
The grey boxes this supersedes are C1_Cafe_Wall*, C1_Cafe_Counter and C1_Street_BuildingN/S.

WHY THE LAYOUT IS SHAPED LIKE THIS - the brief was "between Tokyo and New York", and the two cities are
blended by ZONING rather than by averaging, because averaging them produces a city that is neither:

  * THE LANE IS TOKYO. The 60 m the player actually walks is 10 m wide, which in New York is an alley and in
    Tokyo is an ordinary shopping street. So it is dressed as one: narrow plots of 4 to 8 m, a shop on the
    ground floor of every single building, flats above, signage stacked vertically because the plot is too
    narrow to put it sideways, and the services worn on the outside - air conditioners, cable, a utility pole
    every 12 m. Nothing on the lane is taller than 18 m, so the player can always see the sky.
  * THE SKYLINE IS NEW YORK. Behind and above the lane, at distances the player can never reach, are masonry
    setback towers and curtain-wall slabs of 42 to 62 m with timber water tanks on the roofs. They are what
    the lane is seen against.
  * THE CROSSING IS WHERE THEY MEET, and it is the one piece of layout the story actually requires. The car
    hits the cafe's WEST wall (its box spans x -720..-320, crossing the x = -615 wall line). A car cannot
    arrive from the west unless there is a road to the west - so there is one: a wide avenue running
    north-south at x = -1900, New York in scale, with a corner block on each side of it. That road is why
    the crash is possible, it is what the player sees through the hole for the whole of beat 1, and it is
    the visual handover between the two halves of the city.

The density is deliberately uneven. A prop every two metres reads as a shop display, not as a street; the
lane is dressed in clumps with gaps between them, which is how a real street is actually occupied.
"""
import json, os, random, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'Art', 'Blender', 'export', 'City', 'city_layout.json')

CAFE_X0, CAFE_X1 = -630.0, 630.0
STREET_X0, STREET_X1 = 630.0, 6600.0
STREET_Y = 500.0                 # the facade line, both sides
PLAZA_X0, PLAZA_X1 = 6600.0, 9640.0
PLAZA_Y = 1520.0
RUN_X0, RUN_X1 = 9640.0, 10630.0
AVENUE_X = -1900.0               # the north-south road the car came down

# Keep-clear lanes. Nothing is placed inside these, because the game needs them empty.
#   the walking road down the middle of the lane, and the plaza gate openings
ROAD_HALF = 260.0                # pavement runs from here out to the facade line
GATE_HALF = 300.0

# How much lane each building eats. These are read from the kit's own measured footprints
# (city_models.json) rather than kept by hand here, because the hand-kept copy was wrong the moment the kit
# changed: adding a floor band round each building widened every one of them by 14 cm, the table still said
# the old number, and the tiler laid eleven buildings down overlapping their neighbours. The numbers below
# are only the fallback for when the kit has never been run.
_FALLBACK_WIDTH = {'SM_ShopHouse_A': 614.0, 'SM_ShopHouse_B': 414.0, 'SM_ShopHouse_C': 814.0,
                   'SM_BlockFiller': 1218.0, 'SM_SetbackTower': 1618.0, 'SM_CurtainTower': 1418.0,
                   'SM_PlazaTower': 2018.0, 'SM_CornerBlock': 1400.0}
GAP = 20.0          # a hand's width between neighbours, so nothing ever shares a wall plane


def _load_widths():
    f = os.path.join(ROOT, 'Art', 'Blender', 'export', 'City', 'city_models.json')
    if not os.path.exists(f):
        return dict(_FALLBACK_WIDTH)
    boxes = json.load(open(f, encoding='utf-8'))
    return {m: round(b['x'][1] - b['x'][0], 1) for m, b in boxes.items()}


WIDTH = _load_widths()
for _m, _w in _FALLBACK_WIDTH.items():
    WIDTH.setdefault(_m, _w)

actors = []


def put(label, model, x, y, z=0.0, yaw=0.0):
    actors.append({'label': label, 'model': model, 'x': round(x, 1), 'y': round(y, 1),
                   'z': round(z, 1), 'yaw': round(yaw, 1)})


# ----------------------------------------------------------------- 1. the cafe, and how it is dressed
# These metres come straight from CAFE_DRESS in Art/Blender/jumpcut_city_kit.py, so the mock-up render and
# the level are placing the identical list. Three lanes are kept clear and nothing is allowed into them:
# the player's walk (0,0)->(615,0), the shrapnel's flight (-520,0)->(300,-250), and the driver's body at
# (-380, 220), which the player has to be able to reach and touch.
CAFE_DRESS_CM = [
    # The counter sits at the WEST end with the register on it, beside the wall the car comes through,
    # so the car barely misses whoever is standing at it (Team Owner, Fri Nov 13). Staff side is +Y,
    # facing the car: counter north face y = -200, car south flank y = -100, so the gap is 100 cm and a
    # person at the register stands about 60 cm from the wreck.
    ('SM_CafeCounter', -330.0, -240.0, 0.0, 180), ('SM_CafeRegister', -540.0, -240.0, 110.0, 180),
    ('SM_CafeEspresso', -430.0, -240.0, 104.0, 180),
    ('SM_CafePastryCase', -160.0, -238.0, 104.0, 180), ('SM_CafeShelf', -220.0, -490.0, 2.0, 0),
    ('SM_CafeShelf', 460.0, -490.0, 2.0, 0),
    ('SM_CafeTable', -310.0, 310.0, 2.0, 0), ('SM_CafeChair', -310.0, 235.0, 2.0, 0),
    ('SM_CafeChair', -310.0, 385.0, 2.0, 180),
    ('SM_CafeTable', 10.0, 345.0, 2.0, 0), ('SM_CafeChair', 10.0, 270.0, 2.0, 0),
    ('SM_CafeChair', 10.0, 420.0, 2.0, 180),
    ('SM_CafeTable', 360.0, 310.0, 2.0, 0), ('SM_CafeChair', 360.0, 235.0, 2.0, 0),
    ('SM_CafeChair', 360.0, 385.0, 2.0, 180),
]


def cafe():
    put('City_CafeShell', 'SM_CafeShell', 0, 0, 0, 0)
    for i, (m, x, y, z, yaw) in enumerate(CAFE_DRESS_CM):
        put('City_Cafe_%02d_%s' % (i, m[3:]), m, x, y, z, yaw)
    # Outside the door, on the east face. The awning model projects Blender +Y, which is Unreal -Y, so
    # yaw 90 turns that projection to +X - out over the pavement the player steps onto.
    put('City_CafeAwning', 'SM_CafeAwning', 630, 0, 0, 90)
    put('City_CafeSign', 'SM_CafeSign', 630, -200, 0, 90)
    put('City_CafeMenuBoard', 'SM_CafeMenuBoard', 780, 260, 0, 200)
    put('City_CafeNoren', 'SM_Noren', 648, 0, 0, 90)
    put('City_CafePlanter', 'SM_Planter', 760, -300, 0, 0)
    # The car that came through the west wall, on the exact spot of the two red boxes it replaces
    # (C1_Cafe_Car is centred on (-520, 0) and 400 x 200). Nose east, into the room; the open driver's door
    # is on the +Y side, which is the side his body lies on at (-380, 220).
    put('City_CafeCrashCar', 'SM_CrashCar', -520, 0, 0, 0)


# ----------------------------------------------------------------- 2. the lane the player walks
LANE_MIX = ['SM_ShopHouse_A', 'SM_ShopHouse_B', 'SM_ShopHouse_C', 'SM_ShopHouse_A', 'SM_ShopHouse_B',
            'SM_ShopHouse_A', 'SM_ShopHouse_C', 'SM_ShopHouse_B', 'SM_ShopHouse_A', 'SM_ShopHouse_B',
            'SM_ShopHouse_C', 'SM_ShopHouse_A']


def lane():
    for side, (y, yaw, seed, tag) in enumerate([(-STREET_Y, 0.0, 101, 'S'), (STREET_Y, 180.0, 202, 'N')]):
        rng = random.Random(seed)
        order = LANE_MIX[:]
        rng.shuffle(order)
        x = STREET_X0 + 20.0
        i = 0
        while x < STREET_X1 - 300.0 and i < len(order):
            m = order[i]
            w = WIDTH[m]
            if x + w > STREET_X1:
                break
            put('City_Lane%s_%02d_%s' % (tag, i, m[12:]), m, x + w / 2, y, 0, yaw)
            x += w + GAP
            if rng.random() < 0.28:                       # an alley gap: the lane needs somewhere to breathe
                x += rng.uniform(140.0, 260.0)
            i += 1
        # the kerb and pavement strip: 8 m sections from the facade line in to the road edge
        kx = STREET_X0
        n = 0
        while kx < STREET_X1 - 400.0:
            put('City_Kerb%s_%02d' % (tag, n), 'SM_Kerb', kx + 400.0,
                -ROAD_HALF if side == 0 else ROAD_HALF, 0, 0.0 if side == 0 else 180.0)
            if side == 0:                                 # one strip of painted lines per 8 m of road
                put('City_RoadLines_%02d' % n, 'SM_RoadLines', kx + 400.0, 0.0, 0, 0)
            kx += 800.0
            n += 1
    # Zebra crossings: outside the cafe door, half-way down, and where the lane meets the boss lot.
    for k, zx in enumerate((900.0, 3300.0, 6380.0)):
        put('City_Crosswalk_%d' % k, 'SM_Crosswalk', zx, 0.0, 0, 0)


def lane_props():
    """The clutter, in clumps rather than evenly. Everything sits between the kerb and the facade."""
    rng = random.Random(77)
    wall = 470.0                  # hard against the shopfronts
    mid = 380.0                   # mid-pavement
    edge = 285.0                  # just inside the kerb
    n = 0
    for side, (sgn, yaw_face) in enumerate([(-1.0, 0.0), (1.0, 180.0)]):
        # utility poles every ~11 m, alternating sides, and the cable that spans between them
        px = STREET_X0 + 420.0
        poles = []
        while px < STREET_X1 - 250.0:
            put('City_Pole_%s%02d' % ('SN'[side], len(poles)), 'SM_UtilityPole', px, sgn * edge, 0, 0)
            poles.append(px)
            px += 1120.0
        for k in range(len(poles) - 1):
            a, bx = poles[k], poles[k + 1]
            if bx - a < 1300.0:
                put('City_Cable_%s%02d' % ('SN'[side], k), 'SM_CableSpan', (a + bx) / 2, sgn * edge, 640, 0)
        # street lamps, offset from the poles so they do not stack
        lx = STREET_X0 + 980.0
        while lx < STREET_X1 - 300.0:
            put('City_Lamp_%s%02d' % ('SN'[side], n), 'SM_StreetLamp', lx, sgn * edge, 0, 90 if sgn < 0 else 270)
            lx += 1600.0
            n += 1
        # clumps against the shopfronts
        cx = STREET_X0 + 260.0
        while cx < STREET_X1 - 400.0:
            clump = rng.choice([
                ['SM_VendingMachine', 'SM_VendingMachine'],
                ['SM_VendingMachine', 'SM_CrateStack'],
                ['SM_TrashBags', 'SM_CrateStack'],
                ['SM_Bicycle', 'SM_Bicycle'],
                ['SM_Planter', 'SM_Bench'],
                ['SM_CrateStack'],
                ['SM_TrashBags'],
                ['SM_Bicycle', 'SM_Planter'],
            ])
            ox = 0.0
            for m in clump:
                put('City_Prop_%s%03d_%s' % ('SN'[side], n, m[3:]), m, cx + ox, sgn * wall, 0,
                    yaw_face + rng.choice([-12, 0, 0, 14]))
                ox += rng.uniform(130.0, 190.0)
                n += 1
            cx += rng.uniform(700.0, 1500.0)
        # wall-mounted signage: the thing that actually makes it read as Tokyo
        sx = STREET_X0 + 150.0
        while sx < STREET_X1 - 200.0:
            m = rng.choice(['SM_SignVertical', 'SM_SignVertical', 'SM_SignBlade'])
            put('City_Sign_%s%03d' % ('SN'[side], n), m, sx, sgn * (STREET_Y - 6.0), 0,
                yaw_face + (180 if m == 'SM_SignBlade' and rng.random() < 0.5 else 0))
            sx += rng.uniform(380.0, 820.0)
            n += 1
        # air conditioners and a couple of fire escapes, up the facades
        ax = STREET_X0 + 300.0
        while ax < STREET_X1 - 200.0:
            put('City_AC_%s%03d' % ('SN'[side], n), 'SM_ACUnit', ax, sgn * (STREET_Y - 4.0),
                rng.choice([420.0, 700.0, 1040.0]), yaw_face)
            ax += rng.uniform(420.0, 900.0)
            n += 1
        for fx in (STREET_X0 + 1650.0, STREET_X0 + 4250.0):
            put('City_FireEscape_%s%d' % ('SN'[side], int(fx)), 'SM_FireEscape', fx,
                sgn * (STREET_Y - 4.0), 0, yaw_face)
        # the flat road surface gets manholes and the odd cone, inside the walking lane but low
        for k in range(5):
            put('City_Manhole_%s%d' % ('SN'[side], k), 'SM_Manhole',
                STREET_X0 + 700.0 + k * 1180.0, sgn * rng.uniform(60.0, 200.0), 0, 0)
    # roadworks round the goon fight at x = 4600: it explains why the lane is empty of traffic
    for k, (bx, by, byaw) in enumerate([(4150.0, -150.0, 0.0), (4150.0, 150.0, 0.0), (5050.0, 0.0, 90.0)]):
        put('City_Barrier_%d' % k, 'SM_Barrier', bx, by, 0, byaw)
    for k, (cx2, cy2) in enumerate([(4320.0, -230.0), (4380.0, 220.0), (4980.0, -180.0), (5020.0, 200.0)]):
        put('City_Cone_%d' % k, 'SM_TrafficCone', cx2, cy2, 0, 0)


# ----------------------------------------------------------------- 3. the crossing west of the cafe
def crossing():
    """The avenue the car came down. Seen through the hole in the cafe's west wall for all of beat 1."""
    put('City_CornerNW', 'SM_CornerBlock', AVENUE_X - 700.0, 1500.0, 0, 180)
    put('City_CornerSW', 'SM_CornerBlock', AVENUE_X - 700.0, -1500.0, 0, 90)
    put('City_AvenueTowerA', 'SM_SetbackTower', AVENUE_X - 1500.0, 3400.0, 0, 180)
    put('City_AvenueTowerB', 'SM_CurtainTower', AVENUE_X - 1800.0, -3600.0, 0, 0)
    put('City_AvenueFillA', 'SM_BlockFiller', AVENUE_X - 300.0, 2900.0, 0, 180)
    put('City_AvenueFillB', 'SM_BlockFiller', AVENUE_X - 300.0, -2900.0, 0, 0)
    # the lane's own back wall: the buildings that close the view north and south of the cafe
    put('City_CafeNeighbourN', 'SM_ShopHouse_C', -200.0, 560.0, 0, 180)
    put('City_CafeNeighbourS', 'SM_ShopHouse_A', -250.0, -560.0, 0, 0)
    # THE VIEW THROUGH THE HOLE. The first mock-up render of this looked right and showed nothing: the hole in
    # the west wall is 3 m wide at x = -630, so from inside the cafe it only admits a narrow cone around y = 0,
    # and every avenue building was off to the sides at y = +/-1500 or further. The player would have spent the
    # whole of beat 1 looking through a hole at flat grey. These are the far side of the avenue, ON that axis -
    # which is also simply what you see when you look across a street: the building opposite.
    put('City_AvenueFar_Mid', 'SM_BlockFiller', -3400.0, 0.0, 0, 270)
    put('City_AvenueFar_N', 'SM_ShopHouse_C', -3400.0, 1250.0, 0, 270)
    put('City_AvenueFar_S', 'SM_ShopHouse_A', -3400.0, -1150.0, 0, 270)
    put('City_AvenueFar_Tower', 'SM_SetbackTower', -4600.0, 300.0, 0, 270)
    put('City_AvenueLamp', 'SM_StreetLamp', -2250.0, 260.0, 0, 180)
    put('City_AvenuePole', 'SM_UtilityPole', -2450.0, -380.0, 0, 0)
    put('City_AvenueCone', 'SM_TrafficCone', -1500.0, -120.0, 0, 0)
    put('City_AvenueBarrier', 'SM_Barrier', -1750.0, 180.0, 0, 90)
    put('City_CrossLamp', 'SM_StreetLamp', -1250.0, 520.0, 0, 180)
    put('City_CrossPole', 'SM_UtilityPole', -1300.0, -480.0, 0, 0)
    # the crossing itself, laid across the avenue on the axis the hole looks down
    put('City_CrosswalkAvenue', 'SM_Crosswalk', AVENUE_X, 0.0, 0, 90)


# ----------------------------------------------------------------- 4. the plaza, and the exit
def plaza():
    """The boss arena is a 30 x 30 m walled lot. Give it a building to belong to and it stops being a box."""
    put('City_PlazaTower', 'SM_PlazaTower', 8120.0, PLAZA_Y + 60.0, 0, 180)
    put('City_PlazaTowerW', 'SM_CurtainTower', 6900.0, -PLAZA_Y - 900.0, 0, 0)
    put('City_PlazaTowerE', 'SM_SetbackTower', 9300.0, -PLAZA_Y - 700.0, 0, 0)
    put('City_PlazaFillN', 'SM_BlockFiller', 7000.0, PLAZA_Y + 1900.0, 0, 180)
    # dressing inside the lot, kept out of the gate openings and off the boss's spot at (8120, 0)
    for k, (px, py, pyaw, m) in enumerate([
            (6900.0, -1350.0, 0.0, 'SM_CrateStack'), (6900.0, 1350.0, 180.0, 'SM_CrateStack'),
            (9400.0, -1340.0, 0.0, 'SM_TrashBags'), (9380.0, 1330.0, 180.0, 'SM_Barrier'),
            (7600.0, -1420.0, 0.0, 'SM_Bench'), (8700.0, 1420.0, 180.0, 'SM_Planter'),
            (7300.0, 1400.0, 180.0, 'SM_VendingMachine'), (8900.0, -1400.0, 0.0, 'SM_VendingMachine')]):
        put('City_PlazaProp_%02d' % k, m, px, py, 0, pyaw)
    for k, lx in enumerate((7000.0, 8120.0, 9240.0)):
        for sgn in (-1.0, 1.0):
            put('City_PlazaLamp_%d%s' % (k, 'SN'[sgn > 0]), 'SM_StreetLamp', lx, sgn * 1380.0, 0,
                90 if sgn < 0 else 270)
    # The lot's own walls. One model per grey box, on the same centre, so the arena the fight was tuned
    # in does not move: REPLACES below checks each of these against the box it stands in for.
    # A yard wall's dressed face is its local +Y. Yaw 270 turns that to +X (the west walls face east,
    # into the lot), yaw 90 to -X, yaw 180 to -Y.
    put('City_PlazaWall_W_North', 'SM_YardWall_1250', 6620.0, 875.0, 0, 270)
    put('City_PlazaWall_W_South', 'SM_YardWall_1250', 6620.0, -875.0, 0, 270)
    put('City_PlazaWall_E_North', 'SM_YardWall_1250', 9620.0, 875.0, 0, 90)
    put('City_PlazaWall_E_South', 'SM_YardWall_1250', 9620.0, -875.0, 0, 90)
    put('City_PlazaWall_N', 'SM_YardWall_3040', 8120.0, PLAZA_Y, 0, 180)
    put('City_PlazaWall_S', 'SM_YardWall_3040', 8120.0, -PLAZA_Y, 0, 0)
    # and its floor: a picture of paving laid 1 cm over the real floor, with no collision of its own
    put('City_PlazaPaving', 'SM_PlazaPaving', 8120.0, 0.0, 0, 0)


def exit_run():
    """The 10 m alley past the exit gate, 5 m wide. Close it in: the demo ends on a fade, and a canyon
    reads better for that than an open field does."""
    put('City_RunN_A', 'SM_ShopHouse_B', 9900.0, 430.0, 0, 180)
    put('City_RunN_B', 'SM_ShopHouse_A', 10400.0, 430.0, 0, 180)
    put('City_RunS_A', 'SM_ShopHouse_A', 9930.0, -430.0, 0, 0)
    put('City_RunS_B', 'SM_ShopHouse_B', 10420.0, -430.0, 0, 0)
    put('City_RunTower', 'SM_CurtainTower', 10900.0, 1400.0, 0, 180)
    put('City_RunPole', 'SM_UtilityPole', 9800.0, 210.0, 0, 0)
    put('City_RunCable', 'SM_CableSpan', 10200.0, 210.0, 640, 0)
    put('City_RunTrash', 'SM_TrashBags', 10050.0, -200.0, 0, 0)
    # the corridor's own walls: site hoarding, because the run leads to beat 4's demolition
    put('City_RunWall_N', 'SM_Hoarding_990', 10135.0, 265.0, 0, 180)
    put('City_RunWall_S', 'SM_Hoarding_990', 10135.0, -265.0, 0, 0)


# ----------------------------------------------------------------- 5. the skyline
def near_skyline():
    """The New York tier, pressed right up behind the lane.

    The first mock-up render got this wrong and it is worth recording why: every tower was set back 23 to
    62 m, and from eye height in a 10 m lane with 14 to 18 m shopfronts on both sides, not one of them was
    visible. Half the brief - the New York half - existed in the file and never reached the screen.

    The fix is distance, not size. The lane buildings occupy y 500..1300, so a tower whose facade is at
    y = 1450 stands 1.5 m behind them and rises 28 to 44 m clear of their roofline. It reads over the
    shopfronts along the whole lane and fills the alley gaps, which is exactly where a real dense city
    shows you its towers.
    """
    rng = random.Random(606)
    y = 1450.0
    for sgn in (-1.0, 1.0):
        x = 500.0
        n = 0
        while x < 6300.0:
            m = rng.choice(['SM_SetbackTower', 'SM_CurtainTower', 'SM_CurtainTower', 'SM_SetbackTower'])
            if x + WIDTH[m] > 6300.0:      # the plaza starts at x = 6600: never let a tower into the arena
                break
            put('City_Near_%s%02d' % ('SN'[sgn > 0], n), m, x + WIDTH[m] / 2, sgn * y, 0,
                180.0 if sgn > 0 else 0.0)
            x += WIDTH[m] + GAP + rng.uniform(300.0, 1100.0)
            n += 1


def skyline():
    """Towers at distances the player can never reach, so the skyline has depth behind the near tier.

    Jittered in depth so it reads as layers rather than as one wall of towers at a single distance.
    """
    rng = random.Random(909)
    kinds = ['SM_SetbackTower', 'SM_CurtainTower', 'SM_BlockFiller', 'SM_SetbackTower', 'SM_CurtainTower']
    n = 0
    for sgn in (-1.0, 1.0):
        x = -2600.0
        while x < 11500.0:
            m = rng.choice(kinds)
            depth = rng.choice([3400.0, 4600.0, 6200.0, 8200.0])
            put('City_Sky_%s%02d' % ('SN'[sgn > 0], n), m, x, sgn * depth, 0, 180.0 if sgn > 0 else 0.0)
            x += WIDTH[m] + GAP + rng.uniform(500.0, 1800.0)
            n += 1
    # A landmark straight down the lane's view axis. From the cafe door at x = 615 the player looks east
    # along 60 m of street; putting one tall tower on that line gives him something to walk towards, which
    # is the cheapest piece of level signposting there is - and it is where the skyline finally reads from
    # inside the lane, because it is the one direction that is not blocked by a shopfront.
    # Originally 12600, which put its 14 m footprint across gap 2, B4_P2 and gap 3 - beat 4 did not
    # exist when this line was written. 16200 keeps it on the same view axis (still dead ahead from
    # the cafe door, and 62 m tall so it still reads from the lane) but behind the landing pad.
    put('City_Landmark', 'SM_CurtainTower', 16200.0, 0.0, 0, 0)
    put('City_LandmarkB', 'SM_SetbackTower', 11900.0, -2200.0, 0, 0)
    for k, (rx, ry) in enumerate([(1800.0, -2500.0), (4200.0, 2600.0), (7900.0, -3000.0), (-800.0, 3100.0)]):
        put('City_SkyTank_%d' % k, 'SM_RoofTank', rx, ry, 1900.0, 0)


# ----------------------------------------------------------------- 6. checking it, instead of squinting at it
# Every model's real footprint is written to city_models.json by the Blender kit, so these are measured
# rectangles and not guesses. A render shows you what the camera happens to point at; this looks at all of it.
MODELS_JSON = os.path.join(ROOT, 'Art', 'Blender', 'export', 'City', 'city_models.json')

# (name, x0, x1, y0, y1, what it is for) - rectangles nothing solid may stand in
NO_GO = [
    ('player road', STREET_X0, STREET_X1, -ROAD_HALF, ROAD_HALF, 'the lane the player walks and fights in'),
    ('cafe room', CAFE_X0 + 20, CAFE_X1 - 20, -495.0, 495.0, 'the cafe interior'),
    ('plaza arena', PLAZA_X0 + 60, PLAZA_X1 - 60, -1300.0, 1300.0, 'the boss arena'),
    ('entry gate', 6500.0, 6760.0, -GATE_HALF, GATE_HALF, 'the plaza entry gate opening'),
    ('exit gate', 9500.0, 9760.0, -GATE_HALF, GATE_HALF, 'the plaza exit gate opening'),
    ('exit run', RUN_X0, RUN_X1, -240.0, 240.0, 'the corridor past the exit gate'),
    # Beat 4 was placed in the level on Fri Nov 13 (23:20 UTC), AFTER this layout was first generated,
    # so the checker had no idea it existed and passed a 62 m tower standing in the middle of it.
    # x 11200..14750 is the whole destroyed-building run: B4_P1, both must-blink gaps, B4_P2 and the
    # 10 x 15 m beat-5 landing pad. See tools/beat4_platforming.py.
    ('beat 4 run', 11200.0, 14750.0, -300.0, 300.0,
     'the destroyed-building platforming and the beat-5 landing pad'),
]
# Props that are SUPPOSED to stand in a no-go box (cafe furniture, plaza dressing, road fittings).
ALLOWED_PREFIX = ('City_Cafe', 'City_PlazaProp', 'City_PlazaLamp', 'City_Manhole', 'City_Barrier',
                  'City_Cone', 'City_Kerb', 'City_RunTrash', 'City_RunPole', 'City_RunCable',
                  'City_CafeAwning', 'City_CafeSign', 'City_CafeMenuBoard', 'City_CafeNoren',
                  'City_CafePlanter', 'City_PlazaWall', 'City_PlazaPaving', 'City_RunWall', 'City_RoadLines',
                  'City_Crosswalk')

# Set pieces that stand in for a grey box one-for-one: label -> (the box's label, centre x, centre y,
# size x, size y), straight out of BOXES in tools/c1_layout.py. They are exempt from the no-go check
# above for the same reason the boxes were - a plaza wall is SUPPOSED to stand at the edge of the plaza
# - so they get a stricter one instead: the model may not reach further INTO the play space than
# REPLACE_SLACK past the box it replaces. The fight was tuned inside those boxes.
REPLACE_SLACK = 16.0
REPLACES = {
    'City_CafeCrashCar': ('C1_Cafe_Car', -520.0, 0.0, 400.0, 200.0),
    'City_PlazaWall_W_North': ('C1_Plaza_WallW_North', 6620.0, 875.0, 40.0, 1250.0),
    'City_PlazaWall_W_South': ('C1_Plaza_WallW_South', 6620.0, -875.0, 40.0, 1250.0),
    'City_PlazaWall_E_North': ('C1_Plaza_WallE_North', 9620.0, 875.0, 40.0, 1250.0),
    'City_PlazaWall_E_South': ('C1_Plaza_WallE_South', 9620.0, -875.0, 40.0, 1250.0),
    'City_PlazaWall_N': ('C1_Plaza_WallN', 8120.0, 1520.0, 3040.0, 40.0),
    'City_PlazaWall_S': ('C1_Plaza_WallS', 8120.0, -1520.0, 3040.0, 40.0),
    'City_RunWall_N': ('C1_Run_WallN', 10135.0, 265.0, 990.0, 30.0),
    'City_RunWall_S': ('C1_Run_WallS', 10135.0, -265.0, 990.0, 30.0),
}
# The car's open door is the one deliberate overhang: it swings out of the red box on the +Y side,
# towards the driver's body. What it could get in the way of is checked by name instead (see validate).
REPLACE_OVERHANG_OK = {'City_CafeCrashCar': 'y1'}
CAR_DOOR_FRONT = 56.0       # the door's hinge is this far ahead of the car's origin; nothing of it is further

# Models that are not placed by this layout at all, because they belong INSIDE a Blueprint. Listed here
# so the placer prepares them (Nanite off, collision) with the rest, and so the builder has the swap in
# one place: Blueprint, component, what to set.
BLUEPRINT_MESHES = {
    'SM_PlazaGate': {'blueprint': 'BP_PlazaGate', 'component': 'GateMesh',
                     'set': 'static mesh; relative scale back to (1, 1, 1) - the cube was scaled 0.4 x 5 x 4 '
                            'and this model is already that size, centred on its origin like the cube'},
    'SM_CheckpointPost': {'blueprint': 'BP_Checkpoint', 'component': 'PostMesh',
                          'set': 'static mesh; relative scale (1, 1, 1), relative location z = 0 - it '
                                 'stands on its origin, 229 cm tall'},
    'SM_CheckpointTaken': {'blueprint': 'BP_Checkpoint', 'component': 'TakenSign',
                           'set': 'static mesh; relative scale (1, 1, 1); centred on its origin, 60 x 50 cm, '
                                  'face on local +Y. Keep M_CheckGreen on slot MS_CitySignB if green is wanted'},
    'SM_Shrapnel': {'blueprint': 'BP_Shrapnel', 'component': 'the red bar mesh',
                    'set': 'static mesh; relative scale (1, 1, 1); long axis is local X, 79 cm, centred'},
}


def footprint(a, boxes):
    """World-space x/y rectangle of one placed actor, after its yaw. Yaws here are multiples of 90 plus a
    small decorative jitter, so rotating the corners and taking their bounds is exact enough to trust."""
    import math
    b = boxes[a['model']]
    th = math.radians(a['yaw'])
    cs, sn = math.cos(th), math.sin(th)
    xs, ys = [], []
    for lx in b['x']:
        for ly in b['y']:
            xs.append(a['x'] + lx * cs - ly * sn)
            ys.append(a['y'] + lx * sn + ly * cs)
    return min(xs), max(xs), min(ys), max(ys), b['z']


def validate():
    if not os.path.exists(MODELS_JSON):
        print('! no city_models.json - run the Blender kit once so footprints can be checked')
        return 0
    boxes = json.load(open(MODELS_JSON, encoding='utf-8'))
    problems = []
    unknown = sorted({a['model'] for a in actors if a['model'] not in boxes})
    for m in unknown:
        problems.append('model not in the kit: %s' % m)
    for a in actors:
        if a['model'] not in boxes:
            continue
        x0, x1, y0, y1, zr = footprint(a, boxes)
        if a['label'].startswith(ALLOWED_PREFIX):
            continue
        if zr[0] + a['z'] > 260.0:          # it is mounted above head height: it cannot block anything
            continue
        for nm, bx0, bx1, by0, by1, why in NO_GO:
            if x1 > bx0 and x0 < bx1 and y1 > by0 and y0 < by1:
                problems.append('%s (%s) at (%.0f, %.0f) is inside "%s" - %s'
                                % (a['label'], a['model'], a['x'], a['y'], nm, why))
    # buildings on the lane must not overlap each other along x on the same side
    for side, yv in (('S', -STREET_Y), ('N', STREET_Y)):
        rows = sorted([(footprint(a, boxes), a) for a in actors
                       if a['label'].startswith('City_Lane' + side)], key=lambda r: r[0][0])
        for i in range(len(rows) - 1):
            if rows[i][0][1] > rows[i + 1][0][0] + 1.0:
                problems.append('%s overlaps %s on the %s side of the lane'
                                % (rows[i][1]['label'], rows[i + 1][1]['label'], side))
    # one-for-one replacements must not reach further into the play space than the box they replace
    by_label = {a['label']: a for a in actors}
    for label, (box, cx, cy, sx, sy) in REPLACES.items():
        a = by_label.get(label)
        if a is None:
            problems.append('replacement %s for %s is not in the layout' % (label, box))
            continue
        if a['model'] not in boxes:
            continue
        x0, x1, y0, y1, _ = footprint(a, boxes)
        over = {'x0': (cx - sx / 2) - x0, 'x1': x1 - (cx + sx / 2), 'y0': (cy - sy / 2) - y0,
                'y1': y1 - (cy + sy / 2)}
        for side, d in over.items():
            if d > REPLACE_SLACK and REPLACE_OVERHANG_OK.get(label) != side:
                problems.append('%s reaches %.1f cm past %s on its %s side (slack is %.0f)'
                                % (label, d, box, side, REPLACE_SLACK))
    # the car's open door must leave the driver's body reachable: he lies at (-380, 220) and the player
    # has to get within 220 cm of him and press F, so keep a body's width between him and the door
    car = by_label.get('City_CafeCrashCar')
    if car is not None:
        door_front = car['x'] + CAR_DOOR_FRONT
        if -380.0 - door_front < 60.0:
            problems.append('the crash car door reaches x = %.0f, within 60 cm of the driver at x = -380'
                            % door_front)
    problems += _cafe_dress_agrees()   # the mock-up render and the level must place the identical list
    if problems:
        print('LAYOUT PROBLEMS (%d):' % len(problems))
        for p in problems:
            print('  ! ' + p)
    else:
        print('layout checked: nothing solid stands in the road, the cafe, the arena, the gates or the exit '
              'run, and no two lane buildings overlap')
    return len(problems)


def _cafe_dress_agrees():
    """CAFE_DRESS_CM here vs CAFE_DRESS in Art/Blender/jumpcut_city_kit.py - same list, different units.

    The cafe dressing is written down twice: here in centimetres for the level, and in the Blender kit in
    metres for the mock-up render. They are supposed to be the identical list, and nothing kept them in step,
    so a change made in one and not the other gives a render that quietly disagrees with the game. The counter
    move on Fri Nov 13 touched both; this is what proves it.
    """
    import re
    kit = os.path.join(ROOT, 'Art', 'Blender', 'jumpcut_city_kit.py')
    if not os.path.exists(kit):
        return []
    m = re.search(r'CAFE_DRESS\s*=\s*\[(.*?)\n\]', open(kit, encoding='utf-8').read(), re.S)
    if not m:
        return ['could not find CAFE_DRESS in the Blender kit to compare against']
    rx = r"\('(SM_\w+)',\s*(-?[\d.]+),\s*(-?[\d.]+),\s*(-?[\d.]+),\s*(-?\d+)\)"
    theirs = [(g[0], round(float(g[1]) * 100, 1), round(float(g[2]) * 100, 1), round(float(g[3]) * 100, 1),
               int(g[4])) for g in re.findall(rx, m.group(1))]
    ours = [(r[0], round(r[1], 1), round(r[2], 1), round(r[3], 1), r[4]) for r in CAFE_DRESS_CM]
    if len(ours) != len(theirs):
        return ['the cafe dressing has %d rows here and %d in the Blender kit' % (len(ours), len(theirs))]
    return ['cafe dressing row %d differs: here %s, Blender kit %s' % (i, a, b)
            for i, (a, b) in enumerate(zip(ours, theirs)) if a != b]


def main():
    cafe()
    lane()
    lane_props()
    crossing()
    plaza()
    exit_run()
    near_skyline()
    skyline()
    doc = {
        'units': 'cm',
        'note': 'Unreal world coordinates for Lvl_JumpCut. Z is the actor origin; every model stands on its '
                'own origin at z = 0 except wall-mounted ones, whose geometry starts at its mounting height.',
        'generated_by': 'tools/jumpcut_city_layout.py',
        'generated_at_pacific': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
        'mesh_path': '/Game/Game/Imported/City/',
        'supersedes_greybox': ['C1_Cafe_WallN', 'C1_Cafe_WallS', 'C1_Cafe_WallW', 'C1_Cafe_WallE_South',
                               'C1_Cafe_WallE_North', 'C1_Cafe_Counter', 'C1_Street_BuildingN',
                               'C1_Street_BuildingS'] + sorted({v[0] for v in REPLACES.values()})
                              + ['C1_Cafe_CarCab'],
        # The level's two floor slabs wear M_GreyFloor. The placer's "hide" puts this slot's material on
        # them instead (and "show" puts the grey back) - dark asphalt, which is what makes the painted
        # lines, the crossings and the plaza paving read at all.
        'ground': {'labels': ['Floor_Base', 'C1_Floor_RunExtra'], 'slot': 'MS_CityRoof',
                   'greybox_material': '/Game/Game/Materials/M_GreyFloor'},
        'blueprint_meshes': BLUEPRINT_MESHES,
        'keep_clear': {'road_half_width': ROAD_HALF, 'gate_half_width': GATE_HALF,
                       'player_walk': [[0, 0], [615, 0]], 'shrapnel': [[-520, 0], [300, -250]],
                       'driver_body': [-380, 220], 'boss_spot': [8120, 0]},
        'actors': actors,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(doc, f, indent=1)
        f.write('\n')
    by = {}
    for a in actors:
        by[a['model']] = by.get(a['model'], 0) + 1
    print('wrote %s' % OUT)
    print('actors: %d, distinct models: %d' % (len(actors), len(by)))
    for m in sorted(by, key=lambda k: -by[k]):
        print('  %-20s %d' % (m, by[m]))
    validate()


if __name__ == '__main__':
    main()
