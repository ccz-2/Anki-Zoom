### Anki Zoom v1.1.2 Config:  
All config is effective immediately. If having issues, please click "Restore Defaults".

-   `deckBrowser_zoom_default`: Zoom level that the reset button applies for the deck browser. Must be >`0.2` and <`5`

-   `overview_zoom_default`: Zoom level that the reset button applies for the overview screen (screen after selecting a deck). Must be >`0.2` and <`5`

-   `review_zoom_default`: Zoom level that the reset button applies for card reviews. Must be >`0.2` and <`5`

-   `zoom_step`: How much is zoom is applied per step.  
  Values are a percentage: e.g. `1.1` = 110% scaling on zoom in, (1/1.1)≈91% scaling on zoom out  
  <u>To invert zoom, enter values <1</u>  

-   `scroll_sensitivity`: Defines how much scrolling triggers a zoom step (in arbitrary units). Lower values correlate to more sensitive scrolling.  
  For reference, mousewheels typically emit 120 units per click. High resolution trackpads (Mac + Windows Precision Touchpads) produce a range of values depending on your movement.