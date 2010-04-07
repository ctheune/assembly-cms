===============
Sponsor banners
===============

Design
------

* A separate page type ("sponsor area") which is a sub-type of HTML pages with
  an additional field that defines possible areas where banners can appear

* An extension schema for assets that defines an additional field which can turn
  an asset into a banner and locates it into an area

* A utility/view API that returns a generator of asset variations for a given
  area. It ensures that it does not repeatedly return the same asset. The
  generator will be exhausted if no assets remain.
