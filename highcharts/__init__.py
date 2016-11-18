import pandas as pd
from colour import Color
import pprint
from highcharts import Highchart, Highstock


# ===== #
# UTILS #
# ===== #


def pplot_from_df(df, kind='line', stock=False, y_axes=None, debug=False, **kwargs):
    """

    :param df:    (pd.DataFrame): Column names become series names
    :param kind:   (str or list): Use list of same length as number of cols for multiple plot types
                                 (e.g. ['line_w_col', 'column'])
    :param stock:
    :param y_axes:
    :param debug:         (bool): Pretty prints options json
    :param kwargs:            (): Plotting options such as resolution, labels, color, etc.
    :return:
    """

    # If series given instead of DataFrame, convert:
    df = pd.DataFrame(df)

    # If no columns, do nothing:
    if df.shape[1] == 0:
        print("nothing to plot...")
        return

    # Create a color list for each line to plot:
    if 'colors' not in kwargs:
        kwargs['colors'] = map(
            lambda val: val.get_hex_l(),
            list(Color('#1492FB').range_to(Color('#27662A'), df.shape[1]))
        )

    # Set y axis
    if y_axes is None:
        y_axes = [1] * df.shape[1]
    else:
        assert (len(y_axes) == df.shape[1]), "y_axes must be list of same length as dataframe columns"
        # Should also assert something about the values in this list... later

    # Create highcharts object:
    # (Use height and width if provided):
    if stock:
        hc_visualization = Highstock(**{key: kwargs.pop(key) for key in ['width', 'height'] if key in kwargs})
    else:
        hc_visualization = Highchart(**{key: kwargs.pop(key) for key in ['width', 'height'] if key in kwargs})

    # Set timeseries encoding automatically:
    if df.index.is_all_dates:
        # NOTE *** AFTER monthes, I finally figured out that certain types of option settings
        # were the cause of time not encoding properly.  Basically, customer jinja-js like {x.point} functions
        # need to be created carefully with timestamps in mind.  Also, data must be encoded as 32 bit datetime.
        # (e.g. df.index.map(lambda dt: dt.to_datetime()), or [(datetime.datetime(2016,9,28), $val), ...]
        hc_visualization.set_options('xAxis', {'type': 'datetime'})

    # Set options (chart customization):
    options = get_highchart_options(**kwargs)

    if kind == 'line':
        for col_idx, col in enumerate(df.columns):
            hc_visualization = _highcharts_add_data_set(hc_visualization, df[col], col, kind, y_axes[col_idx])

    elif kind == 'bar' or kind == 'column':
        # Add bar categories (dataframe index):
        options['xAxis']['categories'] = list(df.index)

        # Add grouped column/bar data:
        for col_idx, col in enumerate(df.columns):
            hc_visualization = _highcharts_add_data_set(hc_visualization, df[col], col, kind, y_axes[col_idx])

    elif isinstance(kind, list):

        # Make sure the kind list is the right size:
        assert len(kind) == df.shape[1], "list kind must be the same length as df"

        # If columns in the list, map to line_w_col:
        if 'bar' in kind or 'column' in kind:
            kind = map(lambda a_kind: ("%s_w_col" % a_kind) if a_kind == 'line' else a_kind, kind)

        # Add categories:
        options['xAxis']['categories'] = list(df.index.values)

        # Add grouped data:
        for col_idx, col in enumerate(df.columns):
            hc_visualization = _highcharts_add_data_set(hc_visualization, df[col], col, kind[col_idx], y_axes[col_idx])

    # Set options:
    hc_visualization.set_dict_options(options)

    # Print options json if debug mode is on:
    if debug:
        pp = pprint.PrettyPrinter(indent=1)
        pp.pprint(options)

    return hc_visualization


def _highcharts_add_data_set(H, series, name, chart_type, y_axis):
    """
    Adds data from series by chart type
    :param H:
    :param series:
    :param name:
    :param chart_type:  (str):  {'column', 'bar', 'line', 'line_w_col'}
    :param y_axis:      (int): for multiple y axes, not yet implemented...
    :return:
    """

    # If time series, it must be encoded properly:
    if series.index.is_all_dates:
        index_encoding = lambda val: val.to_datetime()
    else:
        # unity encoding:
        index_encoding = lambda val: val

    if chart_type == 'bar' or chart_type == 'column':
        H.add_data_set(
            list(series.round(2).values),
            type=chart_type,
            name=name
            # color=color_list[idx].get_hex_l()
        )
    elif chart_type == 'line':
        H.add_data_set(
            zip(list(series.index.map(index_encoding)), list(series.values)),
            type=chart_type,
            name=name
            # color=color_list[idx].get_hex_l()
        )
    elif chart_type == 'line_w_col':
        H.add_data_set(
            list(series.values),
            type='line',
            name=name
        )

    return H


def get_highchart_options(
        title='Title',
        subtitle='Subtitle',
        xlabel='xLabel',
        xlim=None,
        xdim=None,
        xtooltipsuffix='',
        xAxis_reversed=False,
        ylabel='yLabel',
        ylim=None,
        ydim=None,
        ytooltipsuffix='',
        yAxis_opposite=False,
        chart_borderColor='#000000',
        chart_borderRadius=0,
        chart_borderWidth=0,
        chart_shadow=False,
        chart_zoomType='xy',
        series_borderWidth=0,
        series_dataLabels_enabled=False,
        legend_align='center',
        legend_enabled=True,
        legend_floating=False,
        legend_itemHoverStyle_color='#000',
        legend_layout='horizontal',
        legend_verticalAlign='bottom',
        legend_width=30,
        tooltip_crosshairs=True,
        tooltip_shared=False,
        buttonOptions_align='left',
        colors='defaults',
        x_plotBands=False,
        xAxis_plotBands={},
        xBand_color='#FCFFC5',
        xBand_from=0,
        xBand_to=5,
        xBand_label='',
        xBand_labelAlign='right',
        xBand_labelColor='#BD0200',
        y_plotBands=False,
        yBand_color='#FCFFC5',
        yBand_from=0,
        yBand_to=5,
        yBand_label='',
        yBand_labelAlign='right',
        yBand_labelColor='#BD0200'
):
    """

    :param title:                       (str):
    :param subtitle:                    (str):
    :param xlabel:                      (str):
    :param xlim:                (float tuple): (min, max)
    :param xdim:                        (str):
    :param ylabel:                      (str):
    :param ylim:                (float tuple): (min, max)
    :param ydim:                        (str):
    :param series_dataLabels_enabled:  (bool):
    :param series_borderWidth:          (int):
    :param legend_enabled:             (bool):
    :param legend_layout:               (str): {'horizontal', 'vertical'}
    :param legend_align:                (str): {'left', 'center', 'right'}
    :param legend_verticalAlign:        (str): {'top', 'middle', 'bottom'}
    :return:
    """

    # Generate mandatory options:
    options = {
        'title': {
            'text': title
        },
        'chart': {
            'borderColor': chart_borderColor,
            'borderWidth': chart_borderWidth,
            'borderRadius': chart_borderRadius,
            'zoomType': chart_zoomType,
            'shadow': chart_shadow
        },
        'subtitle': {
            'text': subtitle
        },
        'xAxis': {
            # 'type': xAxis_type,
            # 'dateTimeLabelFormats': {
            #    'month': '%e. %b',
            #    'year': '%b'
            # },
            'reversed': xAxis_reversed,
            # 'labels': {
            #    'formatter': 'function () {\
            #        return this.value;\
            #    }'
            # },
            'maxPadding': 0.05,
            'showLastLabel': True
        },
        'yAxis': {
            'labels': {
                'formatter': 'function () {\
                    return this.value;\
                }',
                'overflow': 'justify'
            },
            'lineWidth': 2,
            'opposite': yAxis_opposite
        },
        'legend': {
            'enabled': legend_enabled,
            'align': legend_align,
            'verticalAlign': legend_verticalAlign,
            'layout': legend_layout,
            'itemHoverStyle': {
                'color': legend_itemHoverStyle_color
            },
            'width': legend_width,
            'floating': legend_floating
        },
        'tooltip': {
            # 'headerFormat': '<b>{point.x}</b> %s' % xtooltipsuffix,
            # 'headerFormat': '<span style="font-size:11px">{series.name}</span><br>',
            # 'pointFormat': '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.2f}</b> from %s<br/>',
            'pointFormat': '<br><span style="color:{series.color}">{series.name}</span>: {point.y} %s' % ytooltipsuffix,
            'shared': tooltip_shared,
            'crosshairs': tooltip_crosshairs
        },
        'plotOptions': {
            'series': {
                'series_borderWidth': series_borderWidth,
                'dataLabels': {
                    'enabled': series_dataLabels_enabled,
                    'format': '{point.y:.1f}',
                    'color': '#FF0000'
                }
            }
        },
        'navigation': {
            'buttonOptions': {
                'align': buttonOptions_align
            }
        }
    }

    # Add axis labels if probived:
    if xdim is not None:
        options['xAxis']['title'] = {
            'text': "%s (%s)" % (xlabel, xdim)
        }
    else:
        options['xAxis']['title'] = {
            'text': xlabel
        }
    if ydim is not None:
        options['yAxis']['title'] = {
            'text': "%s (%s)" % (ylabel, ydim)
        }
    else:
        options['yAxis']['title'] = {
            'text': ylabel
        }

    # Set axis limits if provided:
    if xlim is not None:
        options['xAxis']['min'] = xlim[0]
        options['xAxis']['max'] = xlim[1]
    if ylim is not None:
        options['yAxis']['min'] = ylim[0]
        options['yAxis']['max'] = ylim[1]

    # Set colors:
    if colors != 'default' and type(colors) is list:
        options['colors'] = colors

    # Create plot bands:
    if x_plotBands:
        """
        options['xAxis']['plotBands'] = {
            'from': xBand_from,
            'to': xBand_to,
            'color': xBand_color,
            'label': {
                'text': xBand_label,
                'align': xBand_labelAlign,
                'textAlign': xBand_labelAlign,
                'color': xBand_labelColor
            }
        }
        """
        options['xAxis']['plotBands'] = xAxis_plotBands
    if y_plotBands:
        options['yAxis']['plotBands'] = {
            'from': yBand_from,
            'to': yBand_to,
            'color': yBand_color,
            'label': {
                'text': yBand_label,
                'align': yBand_labelAlign,
                'textAlign': yBand_labelAlign,
                'color': yBand_labelColor
            }
        }

    return options
