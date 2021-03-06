from text import _WIDTHS, Text

# Text alignments

ALIGN_LEFT = 0
ALIGN_CENTER = 1
ALIGN_RIGHT = 2


class Node:
    '''
    A layout node.
    '''

    def __init__(
            self,
            parent=None,
            layout_width=0,
            layout_height=0,
            wrap_content=False,
            align=ALIGN_LEFT,
            padding=0):

        self.parent = parent
        self.padding = padding
        self.wrap_content = wrap_content
        self.align = align

        if not self.parent and (layout_width == 0 or layout_height == 0):
            raise RuntimeError(
                'Invalid constraints. Must specify parent or a size.')

        if self.parent and layout_width == 0:
            self.layout_width = self.parent.layout_width
        else:
            self.layout_width = layout_width

        if self.parent and layout_height == 0:
            self.layout_height = self.parent.layout_height
        else:
            self.layout_height = layout_height

        self.layout_width -= 2 * self.padding
        self.layout_height -= 2 * self.padding

    def measure(self):
        '''
        Return the measured dimensions.
        '''
        return None, None

    def draw(self, display, x, y):
        pass


class Column(Node):
    '''
    A simple FlowLayout. 
    '''

    def __init__(
        self,
        parent=None,
        layout_width=0,
        layout_height=0,
        wrap_content=True,
        align=ALIGN_LEFT,
        padding=0,
        outline=False
    ):
        super().__init__(
            parent=parent,
            layout_width=layout_width,
            layout_height=layout_height,
            wrap_content=wrap_content,
            align=align,
            padding=padding
        )
        self.outline = outline
        self.children = list()

    def add_node(self, node):
        if isinstance(node, Node):
            self.children.append(node)

    def add_spacer(self, height, outline=False):
        node = Spacer(self, height, outline=outline)
        self.add_node(node)

    def add_text_content(self, content, text_size=3, padding=5, align=ALIGN_LEFT):
        node = TextNode.overflow(
            TextNode(
                parent=self,
                content=content,
                text_size=text_size,
                padding=padding,
                align=align
            ),
            self.layout_width
        )
        self.add_node(node)

    def add_image(
        self,
        image,
        width,
        height,
        wrap_content=True,
        align=ALIGN_LEFT
    ):
        node = ImageNode(
            parent=self,
            image=image,
            width=width,
            height=height,
            wrap_content=wrap_content,
            align=align
        )
        self.add_node(node)

    def measure(self):
        width = 0
        height = 0
        if not self.wrap_content:
            width = self.layout_width
            height = self.layout_height
        else:
            for child in self.children:
                w, h = child.measure()
                w_p = w + self.padding
                width = w_p if width < w_p else width
                height += h + self.padding

        return width, height

    def draw(self, display, x, y):
        # Measure once
        measurements = list()
        for child in self.children:
            measurements.append(child.measure())
        # Adjust x, y coordinates for alignment
        d_x = x
        if self.align == ALIGN_CENTER or self.align == ALIGN_RIGHT:
            # Measure the children in the container
            # to compute the actual intrinsic widths.
            intrinsic_width = 0
            for m in measurements:
                w, _ = m
                intrinsic_width += w

            center_x = int(self.layout_width / 2)
            h_w = int(intrinsic_width / 2)
            if self.align == ALIGN_CENTER:
                d_x += (center_x - h_w)
            else:
                d_x += (self.layout_width - intrinsic_width)
        else:
            d_x += self.padding
        d_y = y + self.padding

        idx = 0
        for child in self.children:
            w, h = measurements[idx]
            outline = getattr(child, 'outline', False)
            if outline:
                display.drawRect(d_x, d_y, w, h, display.BLACK)
            child.draw(display, d_x, d_y)
            d_y += h + self.padding
            idx += 1


class TextNode(Node):
    '''
    A Text Node.
    '''

    def __init__(
            self,
            parent,
            content,
            text_size=3,
            padding=5,
            align=ALIGN_LEFT):

        super().__init__(parent=parent, padding=padding, align=align)
        self.content = content
        self.text_size = text_size
        self.text = Text(
            self.content,
            text_size=self.text_size,
            padding=self.padding
        )

    def measure(self):
        return self.text.measured_width(), self.text.measured_height()

    def draw(self, display, x, y):
        d_x = x
        d_y = y + self.padding
        if self.align == ALIGN_CENTER or self.align == ALIGN_RIGHT:
            width = self.text.measured_width()
            h_w = int(width / 2)
            center_w = int(self.layout_width / 2)
            if self.align == ALIGN_CENTER:
                d_x = x + (center_w - h_w)
            else:
                d_x = x + (self.layout_width - width)
        else:
            d_x = x + self.padding
        display.setTextSize(self.text_size)
        display.printText(
            d_x,
            d_y,
            self.text.content
        )

    @classmethod
    def overflow(cls, node, target_width):
        '''
        This can use a lot of improvement.
        '''

        mw = node.text.measured_width()
        if mw < target_width:
            return node

        index = (target_width // _WIDTHS[node.text_size]) - 4
        ellipsized = node.text.content[:index]
        return TextNode(
            content='%s...' % ellipsized,
            parent=node.parent,
            text_size=node.text_size,
            padding=node.padding
        )


class Row(Node):
    '''
    A Row. (Flow layout in horizontal direction)
    '''

    def __init__(
            self,
            parent=None,
            layout_width=0,
            layout_height=0,
            wrap_content=True,
            align=ALIGN_LEFT,
            padding=0,
            outline=False):

        super().__init__(
            parent=parent,
            layout_width=layout_width,
            layout_height=layout_height,
            wrap_content=wrap_content,
            align=align,
            padding=padding
        )
        self.outline = outline
        self.children = list()

    def measure(self):
        width = 0
        height = 0
        if not self.wrap_content:
            width = self.layout_width
            height = self.layout_height
        else:
            for child in self.children:
                w, h = child.measure()
                h_p = h + self.padding
                width += w + self.padding
                height = h_p if height < h_p else height

        return width, height

    def add_node(self, node):
        if isinstance(node, Node):
            self.children.append(node)

    def add_spacer(self, height, outline=False):
        node = Spacer(self, height, padding=self.padding, outline=outline)
        self.add_node(node)

    def add_text_content(self, content, text_size=3, align=ALIGN_LEFT):
        node = TextNode.overflow(
            TextNode(
                parent=self,
                content=content,
                text_size=text_size,
                align=align
            ),
            self.layout_width
        )
        self.add_node(node)

    def add_image(
        self,
        image,
        width,
        height,
        wrap_content=True,
        align=ALIGN_LEFT
    ):
        node = ImageNode(
            parent=self,
            image=image,
            width=width,
            height=height,
            wrap_content=wrap_content,
            align=align
        )
        self.add_node(node)

    def draw(self, display, x, y):
        # Measure once
        measurements = list()
        for child in self.children:
            measurements.append(child.measure())

        # Adjust x, y coordinates for alignment
        d_x = x
        if self.align == ALIGN_CENTER or self.align == ALIGN_RIGHT:
            # Measure the children in the container
            # to compute the actual intrinsic widths.
            intrinsic_width = 0
            for m in measurements:
                w, _ = m
                intrinsic_width += w

            center_x = int(self.layout_width / 2)
            h_w = int(intrinsic_width / 2)
            if self.align == ALIGN_CENTER:
                d_x += (center_x - h_w)
            else:
                d_x += (self.layout_width - intrinsic_width)
        else:
            d_x += self.padding
        d_y = y + self.padding
        idx = 0
        for child in self.children:
            w, h = measurements[idx]
            outline = getattr(child, 'outline', False)
            if outline:
                display.drawRect(d_x, d_y, w, h, display.BLACK)
            if child.align == ALIGN_CENTER or child.align == ALIGN_RIGHT:
                # Alignments are always with respect to parent
                d_x = x
            child.draw(display, d_x, d_y)
            d_x += w + self.padding
            idx += 1


class Spacer(Node):
    '''
    A Spacer that represents an empty space.
    '''

    def __init__(self, parent, height, padding=0, outline=False):
        # Note: This should not wrap content.
        super().__init__(parent=parent, padding=padding)
        self.width = self.layout_width
        self.height = height
        self.outline = outline

    def measure(self):
        return self.width, self.height

    def draw(self, display, x, y):
        # Does nothing
        pass


class ImageNode(Node):
    '''
    An Image Node
    '''

    def __init__(
            self,
            parent,
            image,
            width,
            height,
            padding=0,
            wrap_content=True,
            align=ALIGN_LEFT):

        super().__init__(
            parent=parent,
            padding=padding,
            wrap_content=wrap_content,
            align=align
        )
        self.image = image
        self.width = width
        self.height = height

    def measure(self):
        if self.wrap_content:
            return self.layout_width, self.layout_height
        else:
            w = self.width + self.padding
            h = self.height + self.padding
            return w, h

    def draw(self, display, x, y):
        d_x = x
        d_y = y + self.padding
        if self.align == ALIGN_CENTER or self.align == ALIGN_RIGHT:
            w = self.width
            h_w = int(w / 2)
            center_w = int(self.layout_width / 2)
            if self.align == ALIGN_CENTER:
                d_x += (center_w - h_w)
            else:
                d_x += (self.layout_width - w)
        else:
            d_x += self.padding
        display.drawBitmap(
            d_x,
            d_y,
            self.image,
            self.width,
            self.height
        )
