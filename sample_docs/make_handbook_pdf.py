"""Generates sample_docs/employee-handbook.pdf from the page text below.
Run once with fpdf2 installed (requirements-dev.txt). Not part of the app.
"""
from pathlib import Path

from fpdf import FPDF

OUT_PATH = Path(__file__).resolve().parent / "employee-handbook.pdf"

# Each page is (title, [(heading, body_text), ...])
PAGES = [
    (
        "Northwind Bike Co. Employee Handbook",
        [
            ("Welcome", (
                "Welcome to Northwind Bike Co. This handbook covers the basics "
                "of working at any of our shop locations: schedules, pay, time "
                "off, and how we expect people to treat each other and our "
                "customers. If something here conflicts with what a manager "
                "tells you, ask HR to sort it out before assuming either one "
                "is wrong."
            )),
            ("Hours and scheduling", (
                "Shop hours are 9am to 7pm Monday through Saturday, and 10am "
                "to 5pm on Sunday. Shifts are posted two weeks in advance on "
                "the schedule board and in the scheduling app. If you need to "
                "swap a shift, find your own coverage first and then notify "
                "your shift lead; swaps are not approved automatically."
            )),
            ("Pay and overtime", (
                "Hourly staff are paid biweekly by direct deposit. Overtime is "
                "paid at 1.5 times normal pay for anything past 40 hours in a "
                "week, calculated on actual hours worked, not scheduled hours. "
                "Commission on bike sales is paid the following pay period "
                "once the sale is finalized and outside the return window."
            )),
        ],
    ),
    (
        "Time off and conduct",
        [
            ("Time off", (
                "Full-time staff accrue one day of paid time off for every "
                "month worked, up to 15 days a year. Part-time staff accrue "
                "PTO on a prorated basis tied to hours worked. Requests for "
                "time off should go in at least two weeks ahead except for "
                "sick time, which can be same-day with a text to your manager."
            )),
            ("Sick leave", (
                "Sick leave is separate from PTO and does not need to be "
                "requested in advance. If you are too sick to work, call or "
                "text your shift lead before your shift starts. Three or more "
                "unplanned sick days in a rolling 30 days triggers a check-in "
                "with HR, not automatic discipline."
            )),
            ("Employee purchase discount", (
                "Employees get 20 percent off bikes and 25 percent off "
                "accessories and apparel, up to a combined 2500 dollars in "
                "discounted purchases per calendar year. The discount is for "
                "personal use and cannot be used to buy inventory for resale."
            )),
            ("Dress code and conduct", (
                "Shop staff wear the provided Northwind polo or fleece during "
                "shifts, with closed-toe shoes required on the sales floor and "
                "in the repair bay. Be straightforward and courteous with "
                "customers and coworkers; harassment or discrimination of any "
                "kind is grounds for immediate termination."
            )),
        ],
    ),
    (
        "Safety and contacts",
        [
            ("Workshop safety", (
                "Safety glasses are required at the truing stand, the wheel "
                "press, and any time you are using a grinder or press tool. "
                "Report any injury to your shift lead the same day, no matter "
                "how minor, so it can be logged. Repair bay floors get slick "
                "with degreaser; wipe spills immediately rather than waiting "
                "for end of shift cleanup."
            )),
            ("Equipment and tools", (
                "Shop tools stay in the shop. Personal tools brought from home "
                "are allowed but not required, and Northwind is not "
                "responsible for damage or loss of personal tools left on "
                "site overnight."
            )),
            ("Who to contact", (
                "For payroll questions, contact HR at the regional office. "
                "For schedule issues, talk to your shift lead first, then the "
                "store manager if it is not resolved. For anything involving "
                "safety or conduct concerns, you can go straight to HR "
                "without going through your manager first."
            )),
        ],
    ),
]


def build():
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    for title, sections in PAGES:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.multi_cell(0, 10, title)
        pdf.ln(4)
        for heading, body in sections:
            pdf.set_font("Helvetica", "B", 12)
            pdf.multi_cell(0, 8, heading)
            pdf.ln(1)
            pdf.set_font("Helvetica", size=11)
            pdf.multi_cell(0, 7, body)
            pdf.ln(4)
    pdf.output(str(OUT_PATH))
    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    build()
