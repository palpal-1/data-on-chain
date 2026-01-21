from yoha_geek_linux_shared.yg_linting.pytest_collect import get_pytest_collect_only_results_string
from cp_file_system import python_module_to_dir
from yoha_geek_linux_shared.yg_linting.file_structure import check_python_package_structure
from syrupy.assertion import SnapshotAssertion
import data_on_chain


def test_pytest_collect(snapshot: SnapshotAssertion) -> None:
    assert get_pytest_collect_only_results_string(python_module_to_dir(data_on_chain)) == snapshot(name=data_on_chain.__name__)


def test_file_structure(snapshot: SnapshotAssertion) -> None:
    res = check_python_package_structure(data_on_chain)
    assert res.whether_succeed == snapshot(name=data_on_chain.__name__ + ".whether_succeed")
    assert res == snapshot(name=data_on_chain.__name__)
