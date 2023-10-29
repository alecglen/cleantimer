from time import sleep
from unittest.mock import patch, MagicMock
from pandas import DataFrame, Series
from pytest import CaptureFixture, raises

from cleantimer.cleantimer import CTimer


def test_ctimer_starts_and_ends_successfully_with_no_exceptions():
    with CTimer("Test"):
        pass


def test_elapsed_time_is_printed_with_precision_1_by_default(capsys: CaptureFixture):
    with CTimer("Test"):
        sleep(0.189123)

    assert capsys.readouterr().out == "Test...done. (0.2s)\n"


def test_elapsed_time_is_printed_with_correct_precision(capsys: CaptureFixture):
    with CTimer("Test", precision=2):
        sleep(0.089123)

    assert capsys.readouterr().out == "Test...done. (0.09s)\n"


def test_child_timer_is_created_with_correct_indentation(capsys: CaptureFixture):
    with CTimer("Parent") as parent_timer:
        with parent_timer.child("Child"):
            pass

    stdout = capsys.readouterr().out
    assert stdout == "Parent...\n\tChild...done. (0.0s)\ndone. (0.0s)\n"


def test_multiple_child_timers_are_indented_correctly(capsys: CaptureFixture):
    with CTimer("Parent") as parent_timer:
        with parent_timer.child("Child1"):
            pass
        with parent_timer.child("Child2"):
            pass

    lines = str(capsys.readouterr().out).split("\n")
    assert len(lines) == 5
    assert lines[0] == "Parent..."
    assert lines[1] == "\tChild1...done. (0.0s)"
    assert lines[2] == "\tChild2...done. (0.0s)"
    assert lines[3] == "done. (0.0s)"
    assert lines[4] == ""


def test_nested_child_timers_are_indented_correctly(capsys: CaptureFixture):
    with CTimer("Parent") as parent_timer:
        with parent_timer.child("Child") as child_timer:
            with child_timer.child("Grandchild"):
                pass

    lines = str(capsys.readouterr().out).split("\n")

    assert len(lines) == 6
    assert lines[0] == "Parent..."
    assert lines[1] == "\tChild..."
    assert lines[2] == "\t\tGrandchild...done. (0.0s)"
    assert lines[3] == "\tdone. (0.0s)"
    assert lines[4] == "done. (0.0s)"
    assert lines[5] == ""


def test_timer_passes_through_exceptions_and_stops_run(capsys: CaptureFixture):
    with raises(TypeError):
        with CTimer("Test Timer"):
            raise TypeError("Test Exception")

    assert capsys.readouterr().out == "Test Timer..."


# def test_precision_is_set_to_zero(capsys: CaptureFixture):
#     with CTimer("Test Timer", precision=0):
#         pass

#     assert capsys.readouterr().out == "Test Timer...done. (0s)\n"


def test_child_timer_message_contains_special_characters(capsys: CaptureFixture):
    with CTimer("Parent") as parent_timer:
        with parent_timer.child("$@!"):
            pass

    assert capsys.readouterr().out == "Parent...\n\t$@!...done. (0.0s)\ndone. (0.0s)\n"


def _action(row):
    return row.A + row.B


def test_progress_apply_succeeds():
    df = DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})

    with CTimer("Test") as timer:
        timer.progress_apply(df, _action)


def test_progress_apply_applies_the_row_operation():
    df = DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})

    with CTimer("Test") as timer:
        result = timer.progress_apply(df, _action)

    assert result.equals(Series([5, 7, 9]))


def test_progress_apply_with_empty_dataframe():
    df = DataFrame()

    with CTimer("Test") as timer:
        with raises(Exception):
            timer.progress_apply(df, _action)


def test_progress_apply_succeeds_with_split():
    df = DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})

    with CTimer("Test") as timer:
        timer.progress_apply(df, _action, split_col="B")


def test_progress_apply_applies_the_row_operation_with_split():
    df = DataFrame({"A": [1, 2, 3, 4], "B": [4, 4, 5, 5]})

    with CTimer("Test") as timer:
        result = timer.progress_apply(df, _action, split_col="B")
        print(result)

    assert list(result) == [5, 6, 8, 9]


def test_progress_apply_prints_header_and_done_statements(capsys: CaptureFixture):
    df = DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})

    with CTimer("Test") as timer:
        timer.progress_apply(df, _action)

    assert capsys.readouterr().out == "Test...\ndone. (0.0s)\n"


@patch("cleantimer.cleantimer.tqdm")
def test_progress_apply_default_renders_single_indented_unnamed_progress_bar(
    mock_tqdm: MagicMock,
):
    df = MagicMock()

    with CTimer("Test") as timer:
        timer.progress_apply(df, _action)

    assert mock_tqdm.pandas.called
    assert mock_tqdm.pandas.call_args[1]["desc"] == "    "

    assert df.progress_apply.call_count == 1
    assert len(df.progress_apply.call_args[0]) == 1
    # pylint: disable-next=comparison-with-callable
    assert df.progress_apply.call_args[0][0] == _action
    assert len(df.progress_apply.call_args[1]) == 1
    assert df.progress_apply.call_args[1]["axis"] == 1


def test_progress_apply_when_split_col_is_defined_renders_partitioned_named_progress_bars(
    capsys: CaptureFixture,
):
    df = DataFrame({"A": [1, 2, 3, 4], "B": [4, 4, 5, 5]})

    with CTimer("Test") as timer:
        timer.progress_apply(df, _action, split_col="B")

    buffer = capsys.readouterr()
    assert buffer.out == "Test...\n\ndone. (0.0s)\n"

    err_lines = buffer.err.split("\n")
    assert len(err_lines) == 3
    assert err_lines[0].startswith(
        "\r    :   0%|          | 0/2 [00:00<?, ?it/s]\r    : 100%|██████████| 2/2"
    )
    assert err_lines[1].startswith(
        "\r    :   0%|          | 0/2 [00:00<?, ?it/s]\r    : 100%|██████████| 2/2"
    )
