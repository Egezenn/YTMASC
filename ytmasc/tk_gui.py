"""
messy, botched, duct-taped, glued gui. looks & feels fine for something you click 2 buttons on though.\n
probably should've done this with classes and stuff but didn't expect it to get this big & conditional
would rewrite the whole thing rather than modify it.
"""

import tkinter as tk
from threading import Thread

from ytmasc.intermediates import (
    check_if_data_exists,
    run_tasks,
    update_library_with_manual_changes_on_files,
)
from ytmasc.parser import parse_library_page, parse_ri_music_db
from ytmasc.utility import library_data


def create_gui():
    root = tk.Tk()
    root.geometry("340x560")

    root.title("YTMASC TK GUI (UNMAINTAINED)")
    validate_cmd = root.register(validate_input)

    parser_plp_rf_state = tk.BooleanVar()
    parser_plp_rf_parameter_show_state = tk.BooleanVar()
    parser_plp_dfa_state = tk.BooleanVar()
    downloader_db_state = tk.BooleanVar(value=True)
    converter_cf_state = tk.BooleanVar(value=True)
    tagger_tf_state = tk.BooleanVar(value=True)

    title_label = tk.Label(root, text="GUI for YTMASC")

    parser_plp_button = tk.Button(
        root,
        text="Parse library page",
        command=lambda: Thread(
            target=lambda: parse_library_page(
                parser_plp_rf_state.get(),
                [
                    int(parser_plp_fp_resend_amount.get()),
                    float(parser_plp_fp_inbetween_delay.get()),
                    float(parser_plp_fp_dialog_wait_delay.get()),
                    float(parser_plp_fp_opening_delay.get()),
                    float(parser_plp_fp_closing_delay.get()),
                    int(parser_plp_fp_save_page_as_index_on_right_click.get()),
                ],
                parser_plp_dfa_state.get(),
            )
        ).start(),
    )
    parser_prmdb_button = tk.Button(
        root,
        text="Parse RiMusic database",
        command=lambda: Thread(target=lambda: parse_ri_music_db()).start(),
    )
    parser_plp_params_label = tk.Label(
        root, text="Parameters for libraryPageOperations"
    )
    parser_plp_rf = tk.Checkbutton(
        root,
        text="Run fetcher",
        variable=parser_plp_rf_state,
        command=lambda: plp_rs_object_toggler(*parser_plp_rf_objects_to_be_toggled),
    )
    parser_plp_rf_argument_show = tk.Checkbutton(
        root,
        text="Show arguments",
        variable=parser_plp_rf_parameter_show_state,
        command=lambda: plp_rs_parameter_show_object_toggler(
            *parser_plp_rf_parameter_show_objects_to_be_toggled
        ),
    )
    parser_plp_rf_warning = tk.Label(root, text="Do not interrupt the process!")

    parser_plp_fp_resend_amount_label = tk.Label(root, text="resendAmount(press):")
    parser_plp_fp_resend_amount = tk.Entry(
        root, validate="key", validatecommand=(validate_cmd, "%P")
    )
    parser_plp_fp_resend_amount.insert(0, "60")
    parser_plp_fp_inbetween_delay_label = tk.Label(root, text="inbetweenDelay(s):")
    parser_plp_fp_inbetween_delay = tk.Entry(
        root, validate="key", validatecommand=(validate_cmd, "%P")
    )
    parser_plp_fp_inbetween_delay.insert(0, "0.2")
    parser_plp_fp_dialog_wait_delay_label = tk.Label(root, text="dialogWaitDelay(s):")
    parser_plp_fp_dialog_wait_delay = tk.Entry(
        root, validate="key", validatecommand=(validate_cmd, "%P")
    )
    parser_plp_fp_dialog_wait_delay.insert(0, "0.5")
    parser_plp_fp_opening_delay_label = tk.Label(root, text="openingDelay(s):")
    parser_plp_fp_opening_delay = tk.Entry(
        root, validate="key", validatecommand=(validate_cmd, "%P")
    )
    parser_plp_fp_opening_delay.insert(0, "6")
    parser_plp_fp_closing_delay_label = tk.Label(root, text="closingDelay(s):")
    parser_plp_fp_closing_delay = tk.Entry(
        root, validate="key", validatecommand=(validate_cmd, "%P")
    )
    parser_plp_fp_closing_delay.insert(0, "3")
    parser_plp_fp_save_page_as_index_on_right_click_label = tk.Label(
        root, text="savePageAsIndexOnRightClick(press):"
    )
    parser_plp_fp_save_page_as_index_on_right_click = tk.Entry(
        root, validate="key", validatecommand=(validate_cmd, "%P")
    )
    parser_plp_fp_save_page_as_index_on_right_click.insert(0, "5")
    parser_plp_dfa = tk.Checkbutton(
        root, text="Delete files after afterwards", variable=parser_plp_dfa_state
    )

    run_tasks_button = tk.Button(
        root,
        text="Run tasks",
        command=lambda: Thread(
            target=lambda: run_tasks(
                downloader_db_state.get(),
                converter_cf_state.get(),
                tagger_tf_state.get(),
            )
        ).start(),
    )
    downloader_db = tk.Checkbutton(
        root, text="Download files", variable=downloader_db_state
    )
    converter_cf = tk.Checkbutton(
        root, text="Convert files after download", variable=converter_cf_state
    )
    tagger_tf = tk.Checkbutton(
        root, text="Tag files after conversion", variable=tagger_tf_state
    )

    parser_plp_rf_objects_to_be_toggled = [
        parser_plp_rf_state,
        parser_plp_rf_parameter_show_state,
        [
            parser_plp_rf_warning,
            parser_plp_rf_argument_show,
            parser_plp_fp_resend_amount_label,
            parser_plp_fp_resend_amount,
            parser_plp_fp_inbetween_delay_label,
            parser_plp_fp_inbetween_delay,
            parser_plp_fp_dialog_wait_delay_label,
            parser_plp_fp_dialog_wait_delay,
            parser_plp_fp_opening_delay_label,
            parser_plp_fp_opening_delay,
            parser_plp_fp_closing_delay_label,
            parser_plp_fp_closing_delay,
            parser_plp_fp_save_page_as_index_on_right_click_label,
            parser_plp_fp_save_page_as_index_on_right_click,
        ],
        parser_plp_rf_objects_to_be_toggled_list_creator(5)[0],
        parser_plp_rf_objects_to_be_toggled_list_creator(5)[1],
    ]
    parser_plp_rf_parameter_show_objects_to_be_toggled = [
        parser_plp_rf_parameter_show_state,
        [
            parser_plp_fp_resend_amount_label,
            parser_plp_fp_resend_amount,
            parser_plp_fp_inbetween_delay_label,
            parser_plp_fp_inbetween_delay,
            parser_plp_fp_dialog_wait_delay_label,
            parser_plp_fp_dialog_wait_delay,
            parser_plp_fp_opening_delay_label,
            parser_plp_fp_opening_delay,
            parser_plp_fp_closing_delay_label,
            parser_plp_fp_closing_delay,
            parser_plp_fp_save_page_as_index_on_right_click_label,
            parser_plp_fp_save_page_as_index_on_right_click,
        ],
        parser_plp_rf_parameter_show_objects_to_be_toggled_list_creator(7)[0],
        parser_plp_rf_parameter_show_objects_to_be_toggled_list_creator(7)[1],
    ]

    tagger_uldwmc = tk.Button(
        root,
        text=f"Update {library_data} with \n manual changes on files",
        command=lambda: Thread(
            target=lambda: update_library_with_manual_changes_on_files()
        ).start(),
    )

    title_label.grid(row=0, column=0, columnspan=2, pady=10, padx=125)
    parser_plp_button.grid(row=1, column=0, columnspan=2, pady=(0, 10))
    parser_prmdb_button.grid(row=2, column=0, columnspan=2, pady=(0, 10))
    parser_plp_params_label.grid(row=3, column=0, columnspan=2)
    parser_plp_rf.grid(row=4, column=0, columnspan=2)
    parser_plp_dfa.grid(row=13, column=0, columnspan=2)
    run_tasks_button.grid(row=14, column=0, columnspan=2, pady=(20, 10))
    downloader_db.grid(row=15, column=0, columnspan=2)
    converter_cf.grid(row=16, column=0, columnspan=2)
    tagger_tf.grid(row=17, column=0, columnspan=2)
    tagger_uldwmc.grid(row=18, column=0, columnspan=2, pady=(10, 10))

    root.mainloop()


def plp_rs_object_toggler(
    checkbutton_state: tk.Variable,
    dependent_checkbutton_state: tk.Variable,
    tkobjects: list[tk.Label, tk.Entry],
    rows: list[int],
    columns: list[int],
):
    if checkbutton_state.get() and dependent_checkbutton_state.get():
        for i, tkobject in enumerate(tkobjects):
            if (i == 0 or i == 1) and checkbutton_state.get():
                tkobject.grid(row=rows[i], column=columns[i], columnspan=2)
            elif i >= 2 and dependent_checkbutton_state.get():
                tkobject.grid(row=rows[i], column=columns[i])

    elif checkbutton_state.get() and not dependent_checkbutton_state.get():
        for i, tkobject in enumerate(tkobjects):
            if (i == 0 or i == 1) and checkbutton_state.get():
                tkobject.grid(row=rows[i], column=columns[i], columnspan=2)
            elif i >= 2 and dependent_checkbutton_state.get():
                tkobject.grid_forget()

    else:
        for i, tkobject in enumerate(tkobjects):
            tkobject.grid_forget()


def plp_rs_parameter_show_object_toggler(
    checkbutton_state: tk.Variable,
    tkobjects: list[tk.Label, tk.Entry],
    rows: list[int],
    columns: list[int],
):
    for i, tkobject in enumerate(tkobjects):
        if checkbutton_state.get():
            tkobject.grid(row=rows[i], column=columns[i])

        else:
            tkobject.grid_forget()


def validate_input(new_value: float) -> bool:
    if new_value == "":
        return True

    try:
        float(new_value)
        return True

    except ValueError:
        return False


# i've got no idea what i did here
# 5
def parser_plp_rf_objects_to_be_toggled_list_creator(i: int) -> list[list[int]]:
    return [
        [
            i,
            i + 1,
            i + 2,
            i + 2,
            i + 3,
            i + 3,
            i + 4,
            i + 4,
            i + 5,
            i + 5,
            i + 6,
            i + 6,
            i + 7,
            i + 7,
        ],
        [0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
    ]  # rows  # columns


# parser_plp_rf_objects_to_be_toggled_list_creator = lambda i: [[i, i + 1, i + 2, i + 2, i + 3, i + 3, i + 4, i + 4, i + 5, i + 5, i + 6, i + 6, i + 7, i + 7],  # rows
#                                                               [0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1]]  # columns


# 7
def parser_plp_rf_parameter_show_objects_to_be_toggled_list_creator(
    i: int,
) -> list[list[int]]:
    return [
        [i, i, i + 1, i + 1, i + 2, i + 2, i + 3, i + 3, i + 4, i + 4, i + 5, i + 5],
        [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
    ]  # rows  # columns
