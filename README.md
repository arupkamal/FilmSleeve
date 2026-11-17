# Film Sleeve QR Label Generator

A small Python desktop application that creates printable PDF sheets of
film-sleeve identification labels. The application uses **Tkinter** for
its graphical interface, **ReportLab** to draw the PDF, and **qrcode**
to generate QR codes.

## 1. Features

-   Generates a one-page PDF containing **nine labels**, arranged in a 3
    × 3 grid.
-   Supports **US Letter** and **A4** paper.
-   Supports **120** and **35 mm** film formats.
-   Supports **negative (NEG)** and **positive (POS)** film.
-   Supports **black & white (BW)** and **colour (COL)** film.
-   Accepts a user-defined prefix and starting serial number.
-   Creates a unique serial for each label, incrementing consecutively.
-   Encodes the complete stock identifier in both the large QR code and
    the miniature QR code.
-   Adds an index grid, label outlines, dotted cutting guides, and a
    generation timestamp.
-   Opens the Tkinter window in the centre of the screen.
-   Lets the user choose the output PDF location through a Save dialog.

## 2. Requirements

### Python

Use Python 3.9 or later. The program uses the Python standard-library
modules:

-   `datetime`
-   `pathlib`
-   `io`
-   `sys`
-   `tkinter`

Tkinter is commonly included with Python on macOS and Windows. On some
Linux distributions, it may need to be installed separately.

### Third-party packages

The generator requires:

-   `reportlab` --- creates the printable PDF.
-   `qrcode` with its Pillow image extra --- creates QR-code images.
-   `Pillow` --- handles QR-code image output; installed by the
    `qrcode[pil]` extra.

Install the dependencies from Terminal:

``` bash
python3 -m pip install reportlab "qrcode[pil]"
```

If `pip` is not available for the selected Python installation, install
or repair that Python distribution first.

## 3. Installation and launch

1.  Save `film_sleeve_labels_tkinter_centered.py` to a convenient
    folder.

2.  Open Terminal.

3.  Change to the folder containing the script. For example:

    ``` bash
    cd ~/Desktop
    ```

4.  Install the dependencies if they are not already installed:

    ``` bash
    python3 -m pip install reportlab "qrcode[pil]"
    ```

5.  Run the application:

    ``` bash
    python3 film_sleeve_labels_tkinter_centered.py
    ```

The **Film Sleeve QR Label Generator** window should open. It is
positioned using the screen and requested window dimensions so that it
appears centred.

### Running from another folder

Use the full path to the script if you are not in its folder. For
example:

``` bash
python3 "/Users/your-user/Desktop/Film Sleeve/sleeve.py"
```

Replace `your-user` and the folder path with the actual location on your
computer.

## 4. Using the graphical interface

### Paper size

Choose the paper stock on which the labels will be printed:

  Option   Description
  -------- ------------------------------------
  Letter   US Letter paper; default selection
  A4       ISO A4 paper

### Film format

  Option       Description
  ------------ -------------------------------------------
  120 film     Medium-format 120 film; default selection
  35 mm film   35 mm film

### Film type

  Option   Description
  -------- ----------------------------------
  NEG      Negative film; default selection
  POS      Positive or reversal film

### Colour mode

  Option   Description
  -------- -----------------------------------------
  BW       Black-and-white film; default selection
  COL      Colour film

### Prefix

Enter a short identifier for the film roll, camera, photographer, or
other naming convention.

-   Required.
-   Between 1 and 20 characters.
-   Automatically converted to uppercase.
-   Cannot contain control characters.

For example, entering `ray` produces the prefix `RAY`.

### Starting serial

Enter the first numeric serial number to use.

-   Must be a whole number.
-   Must be at least `1`.
-   The number is formatted with a minimum of four digits.

For example, a starting serial of `9` produces `0009`. A serial of `125`
produces `0125`. Numbers greater than 9999 are not truncated; they
expand naturally.

### Output PDF

Use **Browse...** to choose the destination and filename for the PDF.
The application proposes a filename based on the selected film settings,
prefix, and starting serial.

If the output field is empty when **Generate PDF** is clicked, the Save
dialog opens automatically. The file is saved as a PDF; if the entered
filename has a different extension, the program changes it to `.pdf`.

### Generate PDF

Click **Generate PDF** to create the sheet. The application validates
the prefix and starting serial before generating the file. A success
dialog reports the output location and the nine serials included on the
page.

Pressing **Return** in the application also invokes the Generate PDF
action.

## 5. Identifier and QR-code format

The printed stock heading and the serial are displayed separately, but
the QR code contains the complete identifier.

The identifier is assembled as:

``` text
{COLOUR}/{FILM_TYPE}{FILM_FORMAT}/{PREFIX}.{SERIAL}
```

Example settings:

-   Colour: `BW`
-   Film type: `NEG`
-   Film format: `120`
-   Prefix: `RAY`
-   Starting serial: `9`

The first label displays:

``` text
BW/NEG120
RAY.0009
```

The large QR code and the miniature QR code both encode exactly:

``` text
BW/NEG120/RAY.0009
```

The next labels use consecutive serials:

``` text
BW/NEG120/RAY.0010
BW/NEG120/RAY.0011
BW/NEG120/RAY.0012
```

Changing the selected options changes the stock portion of the QR
payload. For example, a colour positive 35 mm label with prefix `CAM`
and serial `42` encodes:

``` text
COL/POS35/CAM.0042
```

**Important:** the QR code contains the full stock identifier, not just
the visible serial number.

## 6. PDF sheet layout

### Page arrangement

Each PDF contains one page with nine labels in three columns and three
rows. The complete 3 × 3 label grid is centred on the selected paper
size.

  Element                 Dimension or arrangement
  ----------------------- ---------------------------------------
  Labels per page         9
  Grid                    3 columns × 3 rows
  Individual label        5 cm wide × 6.5 cm high
  Gap between labels      5 mm
  Main QR code            23.4 mm square
  QR-to-serial spacing    2 mm, as designed in the label layout
  Index grid              16.5 mm × 22 mm
  Index grid              3 columns × 3 rows
  Index cell              5.5 mm × approximately 7.33 mm
  Index cell proportion   3:4 width-to-height

### Individual label contents

Each label contains:

1.  **Stock heading** --- for example, `BW/NEG120`.
2.  **Main serial** --- for example, `RAY.0009`.
3.  **Main QR code** --- encodes the complete identifier, such as
    `BW/NEG120/RAY.0009`.
4.  **3 × 3 index grid** --- a miniature QR code followed by eight
    numbered letter positions.
5.  **Timestamp** --- the local date and time at which the PDF was
    generated.

### Index grid

The index grid is read from left to right and top to bottom:

  First cell          Second cell         Third cell
  ------------------- ------------------- -------------------
  Miniature QR        Serial suffix + A   Serial suffix + B
  Serial suffix + C   Serial suffix + D   Serial suffix + E
  Serial suffix + F   Serial suffix + G   Serial suffix + H

The first cell contains a miniature QR code carrying the same complete
identifier as the main QR code.

The other eight cells display only the four-digit serial suffix and its
letter. They do not repeat the prefix. For example, the cells for
`RAY.0009` show `0009` above `A`, `0009` above `B`, and so on through
`H`.

### Cutting guides

The PDF includes:

-   Solid rounded-rectangle outlines around each label.
-   Dotted vertical and horizontal cutting lines centred in the 5 mm
    gutters.
-   A dotted outer boundary positioned 5 mm beyond the outside edges of
    the label grid.

The dotted guides are intended as visual cutting references. Check the
print scale and physical dimensions before cutting a production batch.

## 7. Printing recommendations

For accurate physical dimensions:

1.  Open the generated PDF in a PDF viewer.
2.  Select the correct paper size: Letter or A4.
3.  Print at **Actual Size** or **100% scale**.
4.  Disable options such as **Fit**, **Shrink oversized pages**, or
    automatic scaling.
5.  Print one test sheet.
6.  Measure a label outline. It should be 50 mm × 65 mm.
7.  Confirm that the QR codes scan before printing a larger batch.

Printer margins and printable-area limitations can affect output. If the
printer clips any of the outer guides, check the printer's supported
printable area and paper settings.

## 8. Validation and error handling

The application checks the following input conditions:

  -----------------------------------------------------------------------
  Condition                           Application response
  ----------------------------------- -----------------------------------
  Prefix is empty                     Displays a missing-prefix error

  Prefix exceeds 20 characters        Displays an invalid-prefix error

  Prefix contains control characters  Displays an invalid-prefix error

  Starting serial is not an integer   Displays an invalid-serial error

  Starting serial is less than 1      Displays an invalid-serial error

  PDF generation fails                Displays the underlying error
                                      message

  Save dialog is cancelled            Returns without generating a PDF
  -----------------------------------------------------------------------

The program does not silently substitute a serial number when invalid
input is entered.

## 9. Troubleshooting

### `ModuleNotFoundError: No module named 'reportlab'`

Install ReportLab:

``` bash
python3 -m pip install reportlab
```

### `ModuleNotFoundError: No module named 'qrcode'`

Install qrcode and its image dependency:

``` bash
python3 -m pip install "qrcode[pil]"
```

### Tkinter cannot be imported

Your Python installation may not include Tk support. On macOS, use a
Python distribution that includes Tkinter. On Linux, install the
distribution's Tkinter package (often named `python3-tk`) and try again.

### The window does not appear centred

The script centres the window using the screen dimensions reported by
Tkinter after the widgets have been laid out. Desktop scaling,
multiple-monitor arrangements, window-manager behaviour, or display
changes can affect the apparent position.

### QR code does not scan

-   Make sure the QR code is printed sharply and at 100% scale.
-   Avoid low-quality draft or toner-saving print modes.
-   Ensure that the code is not clipped or covered.
-   Test the PDF on screen as well as on a physical print.
-   Confirm that the scanner is reading the full value, including
    slashes and the dot.

### PDF dimensions look incorrect

Check that the PDF viewer is not scaling the page and that the printer
driver is using the same paper size selected in the application.

## 10. Technical overview

### Libraries and responsibilities

  Module or library   Purpose
  ------------------- -------------------------------------------
  `tkinter` / `ttk`   Desktop GUI and controls
  `filedialog`        Output-file selection
  `messagebox`        Validation, error, and success dialogs
  `datetime`          Local generation timestamp
  `pathlib.Path`      Output path handling
  `io.BytesIO`        Holds generated QR PNG data in memory
  `qrcode`            QR-code creation
  `reportlab`         PDF page, text, shapes, and image drawing
  `Pillow`            QR image conversion and PNG encoding

### Main functions

  -----------------------------------------------------------------------
  Function                            Responsibility
  ----------------------------------- -----------------------------------
  `qr_buffer(value)`                  Creates a QR code and returns it as
                                      an in-memory PNG buffer

  `draw_label(...)`                   Draws one label, including its
                                      heading, serial, QR codes, index
                                      grid, and timestamp

  `draw_guides(...)`                  Draws the dotted cutting guides
                                      around the label sheet

  `create_pdf(...)`                   Calculates page layout and
                                      generates the nine-label PDF

  `main()`                            Builds the Tkinter interface,
                                      validates user input, and launches
                                      PDF generation
  -----------------------------------------------------------------------

### Layout constants

The principal layout settings are defined near the top of the Python
script:

``` python
LABEL_W, LABEL_H = 6 * cm, 8 * cm
GAP = 5 * mm
SERIAL_WIDTH = 4
```

-   `LABEL_W` and `LABEL_H` define the physical label size.
-   `GAP` defines the space between labels.
-   `SERIAL_WIDTH` defines the minimum serial-number padding width.

The main QR-code size, index-grid size, font sizes, line styles, and
spacing are set in the drawing functions.

## 11. Customisation

The following are useful starting points for future changes:

  -----------------------------------------------------------------------
  Desired change                      Where to look
  ----------------------------------- -----------------------------------
  Change label dimensions             `LABEL_W`, `LABEL_H`

  Change spacing between labels       `GAP`

  Change serial padding               `SERIAL_WIDTH`

  Change main QR size                 `qr_size` inside `draw_label()`

  Change index-grid dimensions        `grid_w`, `grid_h` inside
                                      `draw_label()`

  Change label border appearance      Rounded rectangle drawing section
                                      in `draw_label()`

  Change cutting-guide appearance     `draw_guides()`

  Change default radio-button         `StringVar` initial values in
  selections                          `main()`

  Change window title or minimum size Initial setup in `main()`

  Change window centring behaviour    Window geometry section near the
                                      end of `main()`
  -----------------------------------------------------------------------

When changing physical dimensions, review the available space for the
heading, serial, QR code, index grid, and timestamp together. Generate
and measure a test PDF after any layout adjustment.

## 12. Current defaults

When the application starts, the default selections are:

  Setting           Default
  ----------------- ----------------------------
  Paper             Letter
  Film format       120
  Film type         NEG
  Colour mode       BW
  Prefix            Blank; user must enter one
  Starting serial   1

The output file is selected by the user through the Save dialog.

## 13. Quick-start example

To generate nine black-and-white 120 negative labels beginning with
`RAY.0009`:

1.  Select **Letter**.
2.  Select **120 film**.
3.  Select **Negative (NEG)**.
4.  Select **Black & white (BW)**.
5.  Enter `RAY` as the prefix.
6.  Enter `9` as the starting serial.
7.  Click **Browse...** and choose the output filename.
8.  Click **Generate PDF**.
9.  Print the PDF at **100% / Actual Size**.

The resulting sheet contains these serials:

``` text
RAY.0009
RAY.0010
RAY.0011
RAY.0012
RAY.0013
RAY.0014
RAY.0015
RAY.0016
RAY.0017
```

The first label's two QR codes both encode:

``` text
BW/NEG120/RAY.0009
```

------------------------------------------------------------------------

*Documentation corresponds to `film_sleeve_labels_tkinter_centered.py`.*
