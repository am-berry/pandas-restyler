from IPython.core.display import display, HTML, clear_output
from ipywidgets import widgets
from pandas.api.extensions import register_dataframe_accessor, register_series_accessor
import math
from utils import unique_sorted_values_plus_ALL, colour_ge_value, unique_sources
import matplotlib.pyplot as plt
import seaborn as sns

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
        self.dropdown_type = widgets.Dropdown(
            options=unique_sorted_values_plus_ALL(self.df.type),
            description="Filter Type",
        )
        self.dropdown_type.observe(self._dropdown_type_eventhandler, names="value")

        self.dropdown_ip = widgets.Dropdown(
            options=unique_sorted_values_plus_ALL(self.df.ip), description="Filter IP"
        )

        self.dropdown_ip.observe(self._dropdown_ip_eventhandler, names="value")
        self.dropdown_filters = widgets.SelectMultiple(
            options=unique_sources(self.df.sources), description="Sources"
        )

        self.dropdown_filters.observe(self._dropdown_filter_eventhandler, names="value")
        self.dropdown_logged_in = widgets.Dropdown(
            options=unique_sorted_values_plus_ALL(self.df.logged_in),
            description="User logged in",
        )
        self.dropdown_logged_in.observe(
            self._dropdown_logged_in_eventhandler, names="value"
        )
        self.dropdown_trending = widgets.Dropdown(
            options=unique_sorted_values_plus_ALL(self.df.from_trending),
            description="Trending question clicked",
        )
        self.dropdown_trending.observe(
            self._dropdown_trending_eventhandler, names="value"
        )

        self.control = widgets.HBox(
            (
                self.btn_prev,
                self.label,
                self.btn_next,
                self.slider,
                self.dropdown_type,
                self.dropdown_ip,
                self.dropdown_filters,
                self.dropdown_logged_in,
                self.dropdown_trending,
            ),
            layout=widgets.Layout(margin="0 0 50px 0"),
        )
        self.plot_output = widgets.Output()
        self.content = widgets.HTML(self._render_table(self.get_page()))
        self.tab = widgets.Tab([self.content, self.plot_output])
        self.tab.set_title(0, "Dataset Exploration")
        self.tab.set_title(1, "KDE Plot")
        self.dashboard = widgets.VBox(
            [self.control, self.tab], layout=widgets.Layout(margin="0 0 50px 0")
        )

    def get_page(self):
        self.temp_df = self.common_filters(
            self.df,
            self.dropdown_ip.value,
            self.dropdown_type.value,
            self.dropdown_filters.value,
            self.dropdown_logged_in.value,
            self.dropdown_trending.value,
        )
        ret = self.temp_df.iloc[
            self.page * self.pagesize : (self.page + 1) * self.pagesize
        ]
        with self.plot_output:
            sns.kdeplot(self.temp_df.time.dt.hour, shade=True)
            plt.show()
        return ret

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
        display(self.dashboard)
        display(self.control)
        return self

    def _make_clickable(self, val):
        return '<a target="_blank" href="{}">{}</a>'.format(val, val)

    def common_filters(self, df, ip, type_, sources, logged_in, trending):
        if (ip == "ALL") & (type_ == "ALL"):
            common_filter = df
        elif type_ == "ALL":
            common_filter = df[df.ip == ip]
        elif ip == "ALL":
            common_filter = df[df.type == type_]
        else:
            common_filter = df[(df.type == type_) & (df.ip == ip)]

        if not sources or sources[0] == "ALL":
            common_filter = common_filter
        else:
            common_filter = common_filter[
                common_filter.apply(
                    lambda x: True if all(s in x.sources for s in sources) else False,
                    axis=1,
                )
            ]
        if logged_in == "ALL":
            common_filter = common_filter
        else:
            common_filter = common_filter[common_filter["logged_in"] == logged_in]

        if trending == "ALL":
            common_filter = common_filter
        else:
            common_filter = common_filter[common_filter["from_trending"] == trending]

        return common_filter

    def _render_table(self, df):
        try:
            if self.tooltip is not None:
                html = (
                    df.style.use(self._styles)
                    .set_tooltips(self.tooltip)
                    .format({c: self._make_clickable for c in self.clickables})
                    #                    .applymap(lambda x: colour_ge_value(x, num_words), subset=["query"])
                    .set_table_attributes('class="rendered_html"')
                    .render()
                )
            else:
                html = (
                    df.style.use(self._styles)
                    .set_table_attributes('class="rendered_html"')
                    .render()
                )

        except ValueError:
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

    def _dropdown_ip_eventhandler(self, change):
        self.ip = change.new
        self._update()

    def _dropdown_type_eventhandler(self, change):
        self.type_ = change.new
        self._update()

    def _dropdown_filter_eventhandler(self, change):
        self.filter = change.new
        self._update()

    def _dropdown_logged_in_eventhandler(self, change):
        self.logged = change.new
        self._update()

    def _dropdown_trending_eventhandler(self, change):
        self.trending = change.new
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
