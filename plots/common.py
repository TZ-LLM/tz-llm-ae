import os
import matplotlib.font_manager as fm


# font = fm.FontProperties(fname = '/usr/local/share/fonts/Helvetica.ttc')


color_list = ["#268BD2", "#2AA198", "#859900", "#B58900", "#CB4B16", "#DC322F", "#D33682", "#6C71C4"]
bar_color_list = ["#F7FBFF",'#DEEBF7','#C6DBEF','#9ECAE1','#6BAED6','#4292C6','#2171B5','#084594']


def get_figsize(columnwidth, wf=0.5, hf=(5.**0.5-1.0)/2.0, ):
    """Parameters:
    - wf [float]:  width fraction in columnwidth units
    - hf [float]:  height fraction in columnwidth units.
                       Set by default to golden ratio.
    - columnwidth [float]: width of the column in latex. Get this from LaTeX 
                               using \\showthe\\columnwidth
    Returns:  [fig_width,fig_height]: that should be given to matplotlib
      """
    fig_width_pt = columnwidth*wf 
    inches_per_pt = 1.0/72.27               # Convert pt to inch
    fig_width = fig_width_pt*inches_per_pt  # width in inches
#    fig_height = fig_width*hf      # height in inches
    fig_height = columnwidth * hf * inches_per_pt
    return [fig_width, fig_height]


def adjust_ax_style(ax, disable=True):
    if disable:
        ax.tick_params(which="major", length=0, axis="x")
        ax.tick_params(which="minor", length=0, axis="x")
        ax.tick_params(which="minor", length=0, axis="y")
        ax.tick_params(which="major", length=2, axis="y")
    
    ax.tick_params(axis="y", which="major", pad=2)
    # ax.yaxis.set_tick_params(width=0.2)

    for s in ax.spines:
        ax.spines[s].set_linewidth(0.1)

    ax.yaxis.grid(color='black', linestyle=(0, (5, 10)), linewidth=0.1, zorder=0)


def save_figure(fig, name):
    fig.savefig(
        name + ".pdf",
        dpi=1000,
        format="pdf",
        bbox_inches="tight",
    )
    # fig.savefig(
    #     name + ".eps",
    #     dpi=1000,
    #     format="eps",
    #     bbox_inches="tight",
    # )
