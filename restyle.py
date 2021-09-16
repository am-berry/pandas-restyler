from IPython.core.display import display, HTML, clear_output
from ipywidgets import widgets
from pandas.api.extensions import register_dataframe_accessor, register_series_accessor
import math

__version__ = "0.1.0"


class Restyler:
    def __init__(self, df, tooltip=None, clickables=None, pagesize=15, start_page=0):
        self.df = df
        self.tooltip = tooltip
        if clickables:
            self.clickables = clickables
        else:
            self.clickables = []
        self.pagesize = pagesize
        self.page = start_page
        self.max_pages = math.ceil(df.shape[0] / self.pagesize)

        self.btn_next = widgets.Button(description="Next")
        self.btn_next.on_click(self._next_page)

        self.btn_prev = widgets.Button(description="Prev")
        self.btn_prev.on_click(self._prev_page)

        self.label = widgets.Label("PAGE {}/{}".format(self.page + 1, self.max_pages))

        self.slider = widgets.IntSlider(
            value=1,
            max=self.max_pages,
            min=start_page + 1,
            step=1,
        )
        self.slider.observe(self._handle_slider_change, names="value")

        self._styles = []

        self.control = widgets.HBox(
            (
                self.btn_prev,
                self.label,
                self.btn_next,
                self.slider,
            )
        )
        self.content = widgets.HTML(self._render_table(self.get_page()))

    def get_page(self):
        return self.df.iloc[self.page * self.pagesize : (self.page + 1) * self.pagesize]

    @property
    def style(self):
        """
        Get the current page's styler and use it to set the styles to be
        applied when each page is rendered.

        Examples
        --------
        >>> p = Restyler(df)
        >>> p.style = p.style.bar()

        """
        return self.get_page().style

    @style.setter
    def style(self, styler):
        self._styles = styler.export()
        self._update()

    def show(self):
        """
        Display the widget.

        """
        clear_output()
        display(self.control)
        display(self.content)
        display(self.control)
        return self

    def _make_clickable(self, val):
        return '<a target="_blank" href="{}">{}</a>'.format(val, val)

    def _render_table(self, df):
        try:
            if self.tooltip is not None:
                html = (
                    df.style.use(self._styles)
                    .set_tooltips(self.tooltip)
                    .format({c: self._make_clickable for c in self.clickables})
                    .set_table_attributes('class="rendered_html"')
                    .render()
                )
            else:
                html = (
                    df.style.use(self._styles)
                    .set_table_attributes('class="rendered_html"')
                    .render()
                )
        except ValueError as e:
            # Sometimes styling fails (e.g. non-unique indexes).
            # See <https://pandas.pydata.org/pandas-docs/stable/user_guide/
            # style.html#Limitations>.
            # Fall back on default repr.
            html = df._repr_html_()
        return html

    def _update(self):
        self.label.value = "PAGE {}/{}".format(self.page + 1, self.max_pages)
        self.content.value = self._render_table(self.get_page())

    def _handle_slider_change(self, change):
        self.page = change["new"] - 1
        self._update()

    def _next_page(self, b):
        self.page = min(self.max_pages - 1, self.page + 1)
        self.slider.value = self.page + 1
        self._update()

    def _prev_page(self, b):
        self.page = max(0, self.page - 1)
        self.slider.value = self.page + 1
        self._update()


@register_dataframe_accessor("paginate")
class PaginateDataFrameAccessor:
    def __init__(self, pandas_obj):
        self._obj = pandas_obj

    def __call__(self):
        return Restyler(self._obj).show()


@register_series_accessor("paginate")
class PaginateSeriesAccessor:
    def __init__(self, pandas_obj):
        self._obj = pandas_obj

    def __call__(self):
        return Restyler(self._obj.to_frame()).show()
