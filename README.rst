Railworks Dispatcher
====================

Creates a work order by choosing a random scenario from your Railworks folder. Here is
what your work order can look like:

.. image:: docs/_static/example_work_order.png

Don't worry! It is created in vector, so it prints nice.

The scenario briefing and description is taken from
`Armstrong Powerhouse's AP37 Scenario pack <http://www.armstrongpowerhouse.com/index.php?route=product/product&path=29_81&product_id=139>`_.


Setup
-----

* Install Python 3.3+ (this dependency will be removed soon). This project is being developed with Python 3.4.2.

* Place in the same folder as your ``railworks.exe``.


Usage
-----

* Unpack using 7Zip or RW-Tools all the routes and scenarios you want to be scanned.
  Since 2014 DTG have started packing some assets in loseless ZIP files with .ap extension
  which Dispatcher is not able to look through at the moment for performance reasons.
  This has been described in detail by Mike, the author of RW-Tools, in his
  `*.AP file tutorial <http://www.rstools.info/RW_Tools_and_APfiles.pdf>`_.

* Run from console using ``python dispatcher.py`` -
  a uniquely numbered HTML file will be generated in WorkOrders folder inside your Railworks
  installation and opened in your default browser.

* You can also create multiple work orders at once. There are two ways to do this:

  * ``python dispatcher.py 1h`` or ``python dispatcher.py 60m`` - create the orders by
    estimate time you want them to take. Dispatcher will assume you need a 15 minute
    break between scenarios.

  * ``python dispatcher.py 2`` will create a fixed number of scenarios - in this case two


Acknowledgements
----------------

* The created work order uses dot matrix fonts created by
  `Svein Kåre Gunnarson <http://dionaea.com/information/fonts.php>`_.

* The logos of Train Operating Companies are properties of their respective owners.
