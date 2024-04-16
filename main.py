import math
import tkinter as tk


def sort_vertices_clockwise(polygon):
    if not is_clockwise(polygon):
        polygon.reverse()


def is_clockwise(polygon):
    s = 0
    n = len(polygon)
    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % n]
        s += (x2 - x1) * (y2 + y1)
    return s > 0


def is_inside(p1, p2, q):
    r = (p2[0] - p1[0]) * (q[1] - p1[1]) - (p2[1] - p1[1]) * (q[0] - p1[0])
    if r <= 0:
        return True
    else:
        return False


def compute_intersection(p1, p2, p3, p4):
    if p2[0] - p1[0] == 0:
        x = p1[0]

        m2 = (p4[1] - p3[1]) / (p4[0] - p3[0])
        b2 = p3[1] - m2 * p3[0]

        y = m2 * x + b2

    elif p4[0] - p3[0] == 0:
        x = p3[0]

        m1 = (p2[1] - p1[1]) / (p2[0] - p1[0])
        b1 = p1[1] - m1 * p1[0]

        y = m1 * x + b1

    else:
        m1 = (p2[1] - p1[1]) / (p2[0] - p1[0])
        b1 = p1[1] - m1 * p1[0]

        m2 = (p4[1] - p3[1]) / (p4[0] - p3[0])
        b2 = p3[1] - m2 * p3[0]

        x = (b2 - b1) / (m1 - m2)

        y = m1 * x + b1

    intersection = (x, y)

    return intersection


def get_edges_iterator(polygon):
    start_edges = [polygon[-1]] + polygon[:-1]
    end_edges = polygon
    return zip(start_edges, end_edges)


def clip(subject_polygon, clipping_polygon):
    final_polygon = subject_polygon.copy()

    for c_edge_start, c_edge_end in get_edges_iterator(clipping_polygon):

        next_polygon = final_polygon.copy()

        final_polygon = []

        for s_edge_start, s_edge_end in get_edges_iterator(next_polygon):

            if is_inside(c_edge_start, c_edge_end, s_edge_end):
                if not is_inside(c_edge_start, c_edge_end, s_edge_start):
                    intersection = compute_intersection(s_edge_start, s_edge_end, c_edge_start, c_edge_end)
                    final_polygon.append(intersection)
                final_polygon.append(tuple(s_edge_end))
            elif is_inside(c_edge_start, c_edge_end, s_edge_start):
                intersection = compute_intersection(s_edge_start, s_edge_end, c_edge_start, c_edge_end)
                final_polygon.append(intersection)

    return final_polygon


class ClippingWindow:
    def __init__(self, master):
        self.master = master
        self.canvas = tk.Canvas(master, width=400, height=400, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.subject_polygon = []
        self.clip_x = 0
        self.clip_y = 0
        self.drawing_subject = False
        self.drawing_clip = False

        self.button_frame = tk.Frame(master)
        self.button_frame.pack(fill=tk.X, expand=False)

        self.subject_button = tk.Button(self.button_frame, text="Draw Polygon", command=self.toggle_subject)
        self.subject_button.pack(side=tk.LEFT)

        self.clip_button = tk.Button(self.button_frame, text="Draw Clipping Window", command=self.toggle_clip)
        self.clip_button.pack(side=tk.LEFT)

        self.finish_button = tk.Button(self.button_frame, text="Finish Polygon", command=self.finish_polygon)
        self.finish_button.pack(side=tk.LEFT)

        self.clear_button = tk.Button(self.button_frame, text="Clear All", command=self.clear_canvas)
        self.clear_button.pack(side=tk.LEFT)

        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_motion)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def toggle_subject(self):
        self.drawing_subject = True
        self.drawing_clip = False

    def toggle_clip(self):
        self.drawing_clip = True
        self.drawing_subject = False

    def finish_polygon(self):
        if self.drawing_subject and len(self.subject_polygon) > 2:
            self.canvas.create_line(self.subject_polygon[-1][0], self.subject_polygon[-1][1], self.subject_polygon[0][0], self.subject_polygon[0][1],
                                    fill='gray', width=3)
            self.drawing_subject = False

    def clear_canvas(self):
        self.canvas.delete("all")
        self.subject_polygon.clear()

    def on_click(self, event):
        if self.drawing_subject:
            self.subject_polygon.append((event.x, event.y))
            self.draw_point(event.x, event.y)
            if len(self.subject_polygon) > 1:
                self.canvas.create_line(self.subject_polygon[-2][0], self.subject_polygon[-2][1], event.x, event.y, fill='gray', width=3)

        elif self.drawing_clip:
            self.clip_x = event.x
            self.clip_y = event.y

    def on_motion(self, event):
        if self.drawing_clip:
            x0 = self.clip_x
            y0 = self.clip_y
            x1, y1 = event.x, event.y
            self.canvas.delete("clip")
            self.canvas.create_rectangle(x0, y0, x1, y1, outline='red', tag="clip", width=3)

    def on_release(self, event):
        if self.drawing_clip:
            x0 = self.clip_x
            y0 = self.clip_y
            x1, y1 = event.x, event.y

            clip_polygon = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
            sort_vertices_clockwise(clip_polygon)
            if len(self.subject_polygon) > 2:
                subject_polygon = self.subject_polygon.copy()
                sort_vertices_clockwise(subject_polygon)
                clipped_polygon = clip(subject_polygon, clip_polygon)
                self.canvas.delete("clipped")
                self.draw_polygon(clipped_polygon, "green", 5, "clipped")

    def draw_polygon(self, points, color, width, tag):
        for i in range(len(points) - 1):
            self.canvas.create_line(points[i][0], points[i][1], points[i + 1][0], points[i + 1][1], fill=color, width=width, tag=tag)
        self.canvas.create_line(points[-1][0], points[-1][1], points[0][0], points[0][1], fill=color, width=width, tag=tag)

    def draw_point(self, x, y):
        r = 3
        self.canvas.create_oval(x - r, y - r, x + r, y + r, fill='black')


def main():
    root = tk.Tk()
    root.title("Sutherland-Hodgman Polygon Clipping")
    app = ClippingWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
