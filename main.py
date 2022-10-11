import pygame as pg 
import random, sys, os
import matplotlib.path as mplPath
import numpy as np
import pathlib
import math
import random

pg.init()

# Enviroment Variables
run = True
fps = 20
clock = pg.time.Clock()
screen = pg.display.set_mode((700, 700))
icon = pg.transform.scale(pg.image.load("Polygeomer.png"), (30, 30))
pg.display.set_caption("Polygeomer")
print(pg.display.set_icon(icon))

# Interface Variables
selectedObjectColor = (0,255,255)
incompletePolygonColor = (255, 0, 0)
completePolygonColor = (0, 255, 0)
polygonFillColor = (255, 0, 0)
polygonFillColor2 = (0,206,209)
polygonTypeLabelFont = "OpenSans-Regular.ttf"
selectedPoint = None
captureRotateEvent = False
drawEditorInfo = False
changeBackground = False

def CrossProduct(A):
	
	# Stores coefficient of X
	# direction of vector A[1]A[0]
	X1 = (A[1][0] - A[0][0])

	# Stores coefficient of Y
	# direction of vector A[1]A[0]
	Y1 = (A[1][1] - A[0][1])

	# Stores coefficient of X
	# direction of vector A[2]A[0]
	X2 = (A[2][0] - A[0][0])

	# Stores coefficient of Y
	# direction of vector A[2]A[0]
	Y2 = (A[2][1] - A[0][1])

	# Return cross product
	return (X1 * Y2 - Y1 * X2)

# Function to check if the polygon is
# convex polygon or not
def isConvex(points):
	
	# Stores count of
	# edges in polygon
	N = len(points)

	# Stores direction of cross product
	# of previous traversed edges
	prev = 0

	# Stores direction of cross product
	# of current traversed edges
	curr = 0

	# Traverse the array
	for i in range(N):
		
		# Stores three adjacent edges
		# of the polygon
		temp = [points[i], points[(i + 1) % N],
						points[(i + 2) % N]]

		# Update curr
		curr = CrossProduct(temp)

		# If curr is not equal to 0
		if (curr != 0):
			
			# If direction of cross product of
			# all adjacent edges are not same
			if (curr * prev < 0):
				return False
			else:
				
				# Update curr
				prev = curr

	return True


def draw_text(screen: pg.Surface,
              text: str,
              font_file: str,
              font_size: int,
              color: tuple,
              pos: tuple,
              backg=None,
              bold=False,
              italic=False,
              underline=False):
    if '.ttf' in font_file:
        font = pg.font.Font(pathlib.Path(font_file), font_size)
    else:
        font = pg.font.SysFont(font_file, font_size)
    font.set_bold(bold)
    font.set_italic(italic)
    font.set_underline(underline)
    if backg == None:
        t = font.render(text, True, color)
    t = font.render(text, True, color, backg)
    textRect = t.get_rect()
    textRect.center = pos
    screen.blit(t, textRect)


def centroid(vertexes):
    _x_list = [vertex [0] for vertex in vertexes]
    _y_list = [vertex [1] for vertex in vertexes]
    _len = len(vertexes)
    _x = sum(_x_list) / _len
    _y = sum(_y_list) / _len
    return(_x, _y)

def isInsideCircle(circle_x, circle_y, rad, x, y):
    # Compare radius of circle
    # with distance of its center
    # from given point
    if ((x - circle_x) * (x - circle_x) +
        (y - circle_y) * (y - circle_y) <= rad * rad):
        return True
    else:
        return False


class Polygon:
    def __init__(self, points: list, color: tuple, sides_width: int = 2):
        self.visible = True
        self.points = points
        self.color = color
        self.sides_width = sides_width
        self.point_transfer = [] # List of size 2
        self.point_radius = 7
        self.center = None
        self.point_of_rotation = None

    def add_point(self, point: tuple):
        self.points.append(point)

    def set_point_of_rotation(self, point: tuple):
        if len(self.points) > 2:
            self.point_of_rotation = point

    def delete_point(self, p: tuple):
        for point in self.points:
            if isInsideCircle(point[0], point[1], self.point_radius, p[0], p[1]):
                self.points.remove(point)

    def move_point(self, p: tuple):
        if len(self.point_transfer) == 0:
            for point in self.points:
                if isInsideCircle(point[0], point[1], self.point_radius, p[0], p[1]):
                    self.point_transfer.append(point)
        elif len(self.point_transfer) == 1:
            self.point_transfer.append(p)
            self.points[self.points.index(self.point_transfer[0])] = self.point_transfer[1]
            self.point_transfer.clear()

    def rotate(self, degrees):
        """ Rotate polygon the given angle about its center. """
        if degrees != None:
            theta = math.radians(degrees)  # Convert angle to radians
            cosang, sinang = math.cos(theta), math.sin(theta)
            points = self.points
            # find center point of Polygon to use as pivot
            if self.point_of_rotation == None:
                n = len(points)
                cx = sum(p[0] for p in points) / n
                cy = sum(p[1] for p in points) / n
            else:
                if len(self.points) >= 2:
                    cx = self.point_of_rotation[0]
                    cy = self.point_of_rotation[1]

            new_points = []
            for p in points:
                x, y = p[0], p[1]
                tx, ty = x-cx, y-cy
                new_x = ( tx*cosang + ty*sinang) + cx
                new_y = (-tx*sinang + ty*cosang) + cy
                new_points.append((new_x, new_y))

            self.points = new_points

    def draw(self):
        if self.point_of_rotation != None:
            pg.draw.circle(screen, self.vertex_color, self.point_of_rotation, self.point_radius, 0)
        if len(self.points) > 2:
            self.center = centroid(self.points)
        else:
            self.center = None
        if self.visible:
            self.vertex_color = completePolygonColor
            for point in self.points:
                pg.draw.circle(screen, self.vertex_color, point, self.point_radius, 0)
            try:
                for i in range(len(self.points)):
                    pg.draw.line(screen, self.color, self.points[i], self.points[i+1], self.sides_width)
            except IndexError:
                pass
            try:
                if isConvex(self.points):
                    if len(self.points) > 2:
                        pg.draw.polygon(screen, polygonFillColor, self.points, width=0) 
                        draw_text(screen, "Convex", polygonTypeLabelFont, 15, (255,255,255), self.center)
                else:
                    if len(self.points) > 2:
                        pg.draw.polygon(screen, polygonFillColor2, self.points, width=0) 
                        draw_text(screen, "Concave", polygonTypeLabelFont, 15, (255,255,255), self.center)
            except:
                pass
        if self.point_of_rotation != None:
            if len(self.points) > 2:
                pg.draw.circle(screen, (255,255,255), self.point_of_rotation, self.point_radius, 0)


class Layer:
    def __init__(self, name: str, objects: list):
        self.name = name
        self.objects = objects
        self.visible = True

    def add_object(self, object):
        self.objects.append(object)
            
    def update(self):
        # Object visibility is overridden by the Layer's visiblity
        for object in self.objects:
            object.visible = self.visible
            object.draw()

# Editor Variables
drawingColor = (1,1,1)
editorModes = {1: "Edit", 2: "New", 3: "Select"}
editorModeShortcuts = {
    "Edit":"Ctrl + E",
    "New" : "Ctrl + N",
    "Select": "Ctrl + S"
}
editorModeIndex = 1
editorMode = editorModes[editorModeIndex]
LAYERS = [
    Layer("Layer 1", [Polygon([], (1,1,1))])
]
selectedLayerIndex = 0
selectedLayer = LAYERS[selectedLayerIndex]
currentPolygon = selectedLayer.objects[0]
editTypes = {"addPoint":0, "deletePoint":1, "movePoint":2, "Rotate":3, "PointOfRotation":4}
editTypeName = "addPoint"
editorTypeNameShortcuts = {
    "addPoint":"Ctrl + A",
    "deletePoint" : "Ctrl + D",
    "movePoint": "Ctrl + M",
    "Rotate": "Ctrl + R",
    "PointOfRotation":"Ctrl + L"
}
editType = editTypes[editTypeName]
RotationDegrees = 1

screenColors = [
    (0,0,0),
    (255,255,255),
    (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
]
screenImages = [
    "SpaceBackground.jfif"
]

screenFillMode = "Color"
screenImageIndex = 0
screenColorIndex = 0
screenImage = screenImages[screenImageIndex]
screenColor = screenColors[screenColorIndex]

while run:
    clock.tick(fps)
    editorMode = editorModes[editorModeIndex]
    selectedLayer = LAYERS[selectedLayerIndex]
    editType = editTypes[editTypeName]
    try:
        screenImage = screenImages[screenImageIndex]
    except IndexError:
        screenImage = screenImages[0]
    try:
        screenColor = screenColors[screenColorIndex]
    except IndexError:
        screenImage = screenImages[0]
    currentPolygon.color = selectedObjectColor
    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
            pg.quit()
            sys.exit()
        if event.type == pg.MOUSEBUTTONDOWN:
            if editorMode == "Edit":
                mousePosition = pg.mouse.get_pos()
                if editType == 0:
                    currentPolygon.add_point(mousePosition)
                if editType == 1:
                    currentPolygon.delete_point(mousePosition)
                if editType == 2:
                    currentPolygon.move_point(mousePosition)
                if editType == 3:
                    captureRotateEvent = True
                if editType == 4:
                    currentPolygon.set_point_of_rotation(mousePosition)
            if editorMode == "New":
                mousePosition = pg.mouse.get_pos()
                selectedLayer.add_object(Polygon([], (1,1,1)))
                currentPolygon = selectedLayer.objects[-1]
                if editType == 0:
                    currentPolygon.add_point(mousePosition)
                if editType == 1:
                    currentPolygon.delete_point(mousePosition)
                if editType == 2:
                    currentPolygon.move_point(mousePosition)
                if editType == 3:
                    captureRotateEvent = True
                if editType == 4:
                    currentPolygon.set_point_of_rotation(mousePosition)
                editorModeIndex = 1
            if editorMode == "Select":
                mousePosition = pg.mouse.get_pos()
                for polygon in selectedLayer.objects:
                    mPos = pg.mouse.get_pos()
                    try:
                        polygonPoints = mplPath.Path(np.array(polygon.points))
                        polygonSelected = polygonPoints.contains_point(mPos)
                        if polygonSelected:
                            currentPolygon = polygon
                    except ValueError:
                        pass


        if event.type == pg.KEYDOWN:
            if event.key == pg.K_e:
                editorModeIndex = 1
            if event.key == pg.K_n:
                editorModeIndex = 2
            if event.key == pg.K_s:
                editorModeIndex = 3
            if event.key == pg.K_a and pg.key.get_mods() & pg.KMOD_CTRL:
                editTypeName = "addPoint"
            if event.key == pg.K_d and pg.key.get_mods() & pg.KMOD_CTRL:
                editTypeName = "deletePoint"
            if event.key == pg.K_m and pg.key.get_mods() & pg.KMOD_CTRL:
                editTypeName = "movePoint"
            if event.key == pg.K_r and pg.key.get_mods() & pg.KMOD_CTRL:
                editTypeName = "Rotate"
            if event.key == pg.K_l and pg.key.get_mods() & pg.KMOD_CTRL:
                editTypeName = "PointOfRotation"
            if event.key == pg.K_d and pg.key.get_mods() & pg.KMOD_SHIFT:
                drawEditorInfo = not drawEditorInfo
            if event.key == pg.K_b and pg.key.get_mods() & pg.KMOD_CTRL:
                changeBackground = not changeBackground
            if event.key == pg.K_i and pg.key.get_mods() & pg.KMOD_CTRL:
                screenFillMode = "Image"
            if event.key == pg.K_c and pg.key.get_mods() & pg.KMOD_CTRL:
                screenFillMode = "Color"
        

    hold_keys = pg.key.get_pressed()

    if hold_keys[pg.K_RIGHT] and editTypeName == "Rotate" or editTypeName == "PointOfRotation":
        currentPolygon.rotate(RotationDegrees)

    if hold_keys[pg.K_LEFT] and editTypeName == "Rotate" or editTypeName == "PointOfRotation":
        currentPolygon.rotate(-RotationDegrees)

    if hold_keys[pg.K_RETURN] and editTypeName == "Rotate" or editTypeName == "PointOfRotation":
        currentPolygon.rotate(None)

    if not changeBackground:
        if hold_keys[pg.K_UP] and editTypeName == "Rotate" or editTypeName == "PointOfRotation":
            RotationDegrees += 1

        if hold_keys[pg.K_DOWN] and editTypeName == "Rotate" or editTypeName == "PointOfRotation":
            RotationDegrees -= 1
    else:
        if hold_keys[pg.K_UP]:
            if screenFillMode == "Image" and screenImageIndex <= len(screenImages):
                screenImageIndex += 1
            if screenFillMode == "Color" and screenColorIndex <= len(screenColors):
                screenColorIndex += 1

        if hold_keys[pg.K_DOWN]:
            if screenFillMode == "Image" and screenImageIndex >= 0:
                screenImageIndex -= 1
            if screenFillMode == "Color" and screenColorIndex >= 0:
                screenColorIndex -= 1
        
    
                

    # DRAW ALL LAYERS
    if screenFillMode == "Image":
        screen.blit(pg.transform.scale(pg.image.load(screenImage), (700, 700)), (0, 0))
    if screenFillMode == "Color":
        screen.fill((screenColor))
    for layer in LAYERS:
        layer.update()
    if drawEditorInfo:
        draw_text(screen, "Editor Mode:" + "    " + editorMode + "    " + editorModeShortcuts[editorMode], polygonTypeLabelFont, 20, (255,255,255), (150, 30))
        draw_text(screen, "Action:" + "    " + editTypeName + "    " + editorTypeNameShortcuts[editTypeName], polygonTypeLabelFont, 20, (255,255,255),(150, 60))
        draw_text(screen, "Debug Colors:", polygonTypeLabelFont, 20, (255,255,255), (500, 30))
        draw_text(screen, "SelectedObjectColor:", polygonTypeLabelFont, 20, (255,255,255), (500, 60))
        pg.draw.rect(screen, selectedObjectColor, pg.Rect(620, 55, 50, 10))
        draw_text(screen, "ConcavePolygonColor:", polygonTypeLabelFont, 20, (255,255,255), (500, 90))
        pg.draw.rect(screen, polygonFillColor2, pg.Rect(620, 85, 50, 10))
        draw_text(screen, "ConvexPolygonColor:", polygonTypeLabelFont, 20, (255,255,255), (500, 120))
        pg.draw.rect(screen, polygonFillColor, pg.Rect(620, 115, 50, 10))
        draw_text(screen, "VertexColor:", polygonTypeLabelFont, 20, (255,255,255), (500, 150))
        pg.draw.rect(screen, currentPolygon.vertex_color, pg.Rect(620, 145, 50, 10))
        if editTypeName == "Rotate":
            draw_text(screen, f"Rotation Degrees: {RotationDegrees}", polygonTypeLabelFont, 20, (255,255,255), (150, 90))


    pg.display.update()
