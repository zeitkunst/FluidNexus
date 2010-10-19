from setuptools import setup, find_packages
setup(
    name = "fluid_nexus",
    version = "0.2a",
    packages = find_packages(),
    install_requires = [],
    author = "Nicholas Knouf",
    author_email = "fluidnexus@fluidnexus.net",
    description = "Messaging without the mobile phone network",
    license = "GPL v3",
    keywords = "network bluetooth",
    url = "http://fluidnexus.net",
    long_description = "Fluid Nexus is an application for mobile phones and desktops that is primarily designed to enable activists to send messages and data amongst themselves independent of a centralized cellular network.",
    entry_points = {
        'gui_scripts': [
            'fluid_nexus = FluidNexusDesktop:start',
        ]
    }
)
