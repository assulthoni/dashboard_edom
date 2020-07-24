import dash_bootstrap_components as dbc
import dash_html_components as html


def Navbar():
    navbar = dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Kuantitatif", href="/")),
            dbc.NavItem(dbc.NavLink("Kualitatif", href="/kualitatif")),
        ],
        brand="DASHBOARD EDOM DOSEN PRODI SISTEM INFORMASI",
        brand_href="#",
        color="dark",
        dark=True,
        sticky='top'
    )
    return navbar
