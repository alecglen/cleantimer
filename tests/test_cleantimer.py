from time import sleep
from datetime import datetime
from pandas import DataFrame, Series
from pytest import CaptureFixture, raises

from cleantimer.cleantimer import CTimer


now = datetime.now().time().strftime("%-I:%M%p")


def test_ctimer_starts_and_ends_successfully_with_no_exceptions():
    with CTimer("Test"):
        pass


def test_elapsed_time_is_printed_with_precision_1_by_default(capsys: CaptureFixture):
    with CTimer("Test"):
        sleep(0.189123)

    assert capsys.readouterr().out == f"Test ({now})...done. (0.2s)\n"


def test_elapsed_time_is_printed_with_correct_precision(capsys: CaptureFixture):
    with CTimer("Test", precision=2):
        sleep(0.089123)

    assert capsys.readouterr().out == f"Test ({now})...done. (0.09s)\n"


def test_child_timer_is_created_with_correct_indentation(capsys: CaptureFixture):
    with CTimer("Parent") as parent_timer:
        with parent_timer.child("Child"):
            pass

    lines = str(capsys.readouterr().out).split("\n")
    assert len(lines) == 4
    assert lines[0] == f"Parent ({now})..."
    assert lines[1] == f"\tChild ({now})...done. (0.0s)"
    assert lines[2] == "done. (0.0s)"
    assert lines[3] == ""


def test_multiple_child_timers_are_indented_correctly(capsys: CaptureFixture):
    with CTimer("Parent") as parent_timer:
        with parent_timer.child("Child1"):
            pass
        with parent_timer.child("Child2"):
            pass

    lines = str(capsys.readouterr().out).split("\n")
    assert len(lines) == 5
    assert lines[0] == f"Parent ({now})..."
    assert lines[1] == f"\tChild1 ({now})...done. (0.0s)"
    assert lines[2] == f"\tChild2 ({now})...done. (0.0s)"
    assert lines[3] == "done. (0.0s)"
    assert lines[4] == ""


def test_nested_child_timers_are_indented_correctly(capsys: CaptureFixture):
    with CTimer("Parent") as parent_timer:
        with parent_timer.child("Child") as child_timer:
            with child_timer.child("Grandchild"):
                pass

    lines = str(capsys.readouterr().out).split("\n")

    assert len(lines) == 6
    assert lines[0] == f"Parent ({now})..."
    assert lines[1] == f"\tChild ({now})..."
    assert lines[2] == f"\t\tGrandchild ({now})...done. (0.0s)"
    assert lines[3] == "\tdone. (0.0s)"
    assert lines[4] == "done. (0.0s)"
    assert lines[5] == ""


def test_child_timer_uses_its_own_precision(capsys: CaptureFixture):
    with CTimer("Parent") as parent_timer:
        with parent_timer.child("Child", precision=2):
            sleep(0.089123)

    lines = str(capsys.readouterr().out).split("\n")
    assert len(lines) == 4
    assert lines[0] == f"Parent ({now})..."
    assert lines[1] == f"\tChild ({now})...done. (0.09s)"
    assert lines[2] == "done. (0.1s)"
    assert lines[3] == ""


def test_timer_passes_through_exceptions_and_stops_run(capsys: CaptureFixture):
    with raises(TypeError):
        with CTimer("Test Timer"):
            raise TypeError("Test Exception")

    assert capsys.readouterr().out == f"Test Timer ({now})..."


def test_precision_is_set_to_zero(capsys: CaptureFixture):
    with CTimer("Test Timer", precision=0):
        pass

    assert capsys.readouterr().out == f"Test Timer ({now})...done. (0s)\n"


def test_message_contains_special_characters(capsys: CaptureFixture):
    with CTimer("$@!"):
        pass

    assert capsys.readouterr().out == f"$@! ({now})...done. (0.0s)\n"


df = DataFrame({"A": [1, 2, 3, 4], "B": [4, 4, 5, 5]})


def _action(row):
    return row.A + row.B


def test_progress_apply_succeeds():
    with CTimer("Test") as timer:
        timer.progress_apply(df, _action)


def test_progress_apply_applies_the_row_operation():
    with CTimer("Test") as timer:
        result = timer.progress_apply(df, _action)

    assert result.equals(Series([5, 6, 8, 9]))


def test_progress_apply_with_empty_dataframe():
    empty_df = DataFrame()

    with CTimer("Test") as timer:
        with raises(Exception):
            timer.progress_apply(empty_df, _action)


def test_progress_apply_prints_header_and_done_statements(capsys: CaptureFixture):
    with CTimer("Test") as timer:
        timer.progress_apply(df, _action)

    assert capsys.readouterr().out == f"Test ({now})...\ndone. (0.0s)\n"


def test_progress_apply_default_logs_single_indented_unnamed_progress_bar(
    capsys: CaptureFixture,
):
    with CTimer("Test") as timer:
        timer.progress_apply(df, _action)

    buffer = capsys.readouterr()
    assert buffer.out == f"Test ({now})...\ndone. (0.0s)\n"

    err_lines = buffer.err.split("\n")
    assert len(err_lines) == 2
    assert err_lines[0].startswith(
        "\r    :   0%|          | 0/4 [00:00<?, ?it/s]\r    : 100%|██████████| 4/4"
    )


def test_progress_apply_with_message_logs_named_progress_bar(
    capsys: CaptureFixture,
):
    with CTimer("Test") as timer:
        timer.progress_apply(df, _action, message="TestBar")

    buffer = capsys.readouterr()
    assert buffer.out == f"Test ({now})...\ndone. (0.0s)\n"

    err_lines = buffer.err.split("\n")
    assert len(err_lines) == 2
    assert err_lines[0].startswith(
        "\r    TestBar:   0%|          | 0/4 [00:00<?, ?it/s]\r    TestBar: 100%|██████████| 4/4"
    )


def test_progress_apply_succeeds_with_split():
    with CTimer("Test") as timer:
        timer.progress_apply(df, _action, split_col="B")


def test_progress_apply_applies_the_row_operation_with_split():
    with CTimer("Test") as timer:
        result = timer.progress_apply(df, _action, split_col="B")

    assert list(result) == [5, 6, 8, 9]


def test_progress_apply_when_split_col_is_defined_logs_partitioned_named_progress_bars(
    capsys: CaptureFixture,
):
    with CTimer("Test") as timer:
        timer.progress_apply(df, _action, split_col="B")

    buffer = capsys.readouterr()
    assert buffer.out == f"Test ({now})...\n\ndone. (0.0s)\n"

    err_lines = buffer.err.split("\n")
    assert len(err_lines) == 3
    assert err_lines[0].startswith(
        "\r    4:   0%|          | 0/2 [00:00<?, ?it/s]\r    4: 100%|██████████| 2/2"
    )
    assert err_lines[1].startswith(
        "\r    5:   0%|          | 0/2 [00:00<?, ?it/s]\r    5: 100%|██████████| 2/2"
    )


def test_progress_apply_with_split_and_message_logs_partitioned_named_progress_bars(
    capsys: CaptureFixture,
):
    with CTimer("Test") as timer:
        timer.progress_apply(df, _action, split_col="B", message="Mult {}")

    buffer = capsys.readouterr()
    assert buffer.out == f"Test ({now})...\n\ndone. (0.0s)\n"

    err_lines = buffer.err.split("\n")
    assert len(err_lines) == 3
    assert err_lines[0].startswith(
        "\r    Mult 4:   0%|          | 0/2 [00:00<?, ?it/s]\r    Mult 4: 100%|██████████| 2/2"
    )
    assert err_lines[1].startswith(
        "\r    Mult 5:   0%|          | 0/2 [00:00<?, ?it/s]\r    Mult 5: 100%|██████████| 2/2"
    )
