import sys
import getopt

sys.path.append(".")  # noqa

from sis.test_data import create_01_major
from sis.test_data import create_02_admin
from sis.test_data import create_03_semester
from sis.test_data import create_04_student
from sis.test_data import create_06_semesterstudent
from sis.test_data import create_08_professor
from sis.test_data import create_20_course
from sis.test_data import create_22_majorprerequisites
from sis.test_data import create_25_courseprerequisites
from sis.test_data import create_27_reference_items
from sis.test_data import create_30_section
from sis.test_data import create_32_sectionreferenceitem
from sis.test_data import create_40_sectionstudent

modules = [
    (
        1,
        create_01_major,
    ),
    (
        2,
        create_02_admin,
    ),
    (
        3,
        create_03_semester,
    ),
    (
        4,
        create_04_student,
    ),
    (
        6,
        create_06_semesterstudent,
    ),
    (
        8,
        create_08_professor,
    ),
    (
        20,
        create_20_course,
    ),
    (
        22,
        create_22_majorprerequisites,
    ),
    (
        25,
        create_25_courseprerequisites,
    ),
    (
        27,
        create_27_reference_items,
    ),
    (
        30,
        create_30_section,
    ),
    (
        32,
        create_32_sectionreferenceitem,
    ),
    (
        40,
        create_40_sectionstudent,
    ),
]


def main(argv):
    next = 0
    last = 999
    doit = None
    spec = 'test_data [ --create | --delete | --list ] [--start <num> --stop <num>' + \
           ' | --only <num>]'
    try:
        opts, args = getopt.getopt(argv, "hclds:o:",
                                   ["list", "create", "start=", "stop=", "delete", "only="])
    except getopt.GetoptError:
        print(spec)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(spec)
            sys.exit()
        elif opt in ("-l", "--list"):
            for mod in modules:
                print(f'{mod[0]} - {mod[1]}')
            sys.exit()
        elif opt in ("-s", "--start"):
            next = int(arg)
        elif opt in ("--stop"):
            last = int(arg)
        elif opt in ("--only"):
            next = int(arg)
            last = int(arg)
        elif opt in ("-c", "--create"):
            doit = 'create'
        elif opt in ("-d", "--delete"):
            doit = 'delete'
    if not doit:
        print('You probably want "--create" to add data to a clean database. ' +
              'Do a "--list" to see modules')
        print(spec)
        exit()

    if len(args):
        print('You have leftover arguments. Cowardly refusing to proceed.')
        print(spec)
        exit()

    if next > last:
        (next, last) = (last, next)

    print(doit[0:-1] + "ing test data")
    if doit == 'create':
        for mod in modules:
            if next <= mod[0] <= last:
                next = mod[0] + 1
                print(f'********************** about to {doit} {mod[0]}:')
                mod[1].createData()
                print(f'********************** done {mod[0]}:')
    else:
        (next, last) = (last, next)
        modules.reverse()
        for mod in modules:
            if next >= mod[0] >= last:
                next = mod[0] - 1
                print(f'********************** about to {doit} {mod[0]}:')
                mod[1].cleanData()
                print(f'********************** done {mod[0]}:')


if __name__ == "__main__":
    main(sys.argv[1:])
