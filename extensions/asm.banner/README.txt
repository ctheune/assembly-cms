=====================
Advertisement banners
=====================



Design
------

An extension to manage banner images which can be dynamically embedded in a
page's layout.

- Manage banner images with a URL, an alternative text, an area,

- An area defines the number of banners shown in this area.

- A persistent utility IBannerChooser provides a method `chooseBanners` which
  returns a list of banners (specifically assets) based on the criteria for which slot it
  is intended.

- The utility is installed automatically into all sites (existing and new) but
  is not part of the site.

- The utility contains the banners, but the banners are not part of the site
  content (watch out for indexing).

- The utility needs to show up somewhere in navigation. -> actions viewlet
