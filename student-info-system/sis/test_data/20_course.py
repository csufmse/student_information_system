import os
import sys

import django

sys.path.append(".")  # noqa
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")  # noqa
django.setup()  # noqa

from random import randint

from sis.models import Course, Major

to_generate = 150

specs = (
    ('101', 'Underwater Basketweaving', 'The Career, The Myth', '5.0'),
    ('151', 'The Bandicoot', 'The Bandicoot but more so', '5.0'),
    ('146', 'The Snow leopard', 'The Snow leopard but more so', '3.0'),
    ('258', 'The Kite and their Refractory Engineer',
     'The Kite and their Refractory Engineer but more so', '4.0'),
    ('380', 'The Crane for Ambulance Controller',
     'The Crane for Ambulance Controller but more so', '3.0'),
    ('423', 'The Ringneck dove', 'The Ringneck dove but more so', '3.0'),
    ('179', 'The Pony for Administrator', 'The Pony for Administrator but more so', '3.0'),
    ('536', 'The Octopus', 'The Octopus but more so', '3.0'),
    ('368', 'The Viper training for the Instrument Engineer',
     'The Viper training for the Instrument Engineer but more so', '4.0'),
    ('187', 'The Gorilla', 'The Gorilla but more so', '2.0'),
    ('540', 'The Giraffe as Tax Inspector', 'The Giraffe as Tax Inspector but more so', '3.0'),
    ('326', 'Getting to the Bottom of the  Vampire squid and the Racehorse Groom',
     'Getting to the Bottom of the  Vampire squid and the Racehorse Groom but more so', '3.0'),
    ('377', 'The Reptile', 'The Reptile but more so', '4.0'),
    ('248', 'The Booby training for the Body Fitter',
     'The Booby training for the Body Fitter but more so', '3.0'),
    ('528', 'The Hyena as Assistant Teacher', 'The Hyena as Assistant Teacher but more so',
     '4.0'),
    ('549', 'The Siamese fighting fish training for the Aircraft Designer',
     'The Siamese fighting fish training for the Aircraft Designer but more so', '4.0'),
    ('490', 'The Giraffe as Aircraft Maintenance Engineer',
     'The Giraffe as Aircraft Maintenance Engineer but more so', '3.0'),
    ('362', 'Independent Study: the  Junglefowl',
     'Independent Study: the  Junglefowl but more so', '4.0'),
    ('150', 'The Cardinal', 'The Cardinal but more so', '3.0'),
    ('221', 'Reading topics in the  Junglefowl instead of the Sportsman',
     'Reading topics in the  Junglefowl instead of the Sportsman but more so', '3.0'),
    ('350', 'The Shrew', 'The Shrew but more so', '3.0'),
    ('455', 'Composition of the  Booby', 'Composition of the  Booby but more so', '3.0'),
    ('516', 'The Sea snail and the Student Nurse',
     'The Sea snail and the Student Nurse but more so', '3.0'),
    ('339', 'The Parakeet', 'The Parakeet but more so', '3.0'),
    ('287', 'The Black widow spider and the Charity Worker',
     'The Black widow spider and the Charity Worker but more so', '3.0'),
    ('527', 'The Wasp as Marble Mason', 'The Wasp as Marble Mason but more so', '4.0'),
    ('227', 'Composition of the  Mandrill', 'Composition of the  Mandrill but more so', '3.0'),
    ('472', 'The Blue bird and the Plumber', 'The Blue bird and the Plumber but more so', '2.0'),
    ('126', 'The Piranha instead of the Car Wash Attendant',
     'The Piranha instead of the Car Wash Attendant but more so', '5.0'),
    ('264', 'Lecture Topics in the  Salmon instead of the Recreational',
     'Lecture Topics in the  Salmon instead of the Recreational but more so', '2.0'),
    ('108', 'The Baboon training for the Trade Mark Agent',
     'The Baboon training for the Trade Mark Agent but more so', '3.0'),
    ('173', 'The Catfish', 'The Catfish but more so', '4.0'),
    ('413', 'The Goat and their Shot Blaster', 'The Goat and their Shot Blaster but more so',
     '4.0'),
    ('429', 'The Mosquito', 'The Mosquito but more so', '4.0'),
    ('545', 'The Bird instead of the Publicity Manager',
     'The Bird instead of the Publicity Manager but more so', '4.0'),
    ('380', 'The Amphibian for Probation Worker',
     'The Amphibian for Probation Worker but more so', '4.0'),
    ('210', 'The Alpaca', 'The Alpaca but more so', '4.0'),
    ('299', 'The Vole', 'The Vole but more so', '3.0'),
    ('279', 'The Whitefish', 'The Whitefish but more so', '4.0'),
    ('473', 'The Coral', 'The Coral but more so', '4.0'),
    ('121', 'Survey on the  Right whale exploring the Legal Secretary',
     'Survey on the  Right whale exploring the Legal Secretary but more so', '3.0'),
    ('306', 'Programming the  Sea snail exploring the Camera Repairer',
     'Programming the  Sea snail exploring the Camera Repairer but more so', '4.0'),
    ('497', 'The Crane', 'The Crane but more so', '3.0'),
    ('106', 'The Orangutan and their Textile Worker',
     'The Orangutan and their Textile Worker but more so', '3.0'),
    ('317', 'Reading topics in the  Marten', 'Reading topics in the  Marten but more so', '3.0'),
    ('221', 'Deconstruction of  the  Whooping crane as symbol for the Tool Maker',
     'Deconstruction of  the  Whooping crane as symbol for the Tool Maker but more so', '4.0'),
    ('419', 'Seminar on the  Yellow perch for Aeronautical Engineer',
     'Seminar on the  Yellow perch for Aeronautical Engineer but more so', '3.0'),
    ('353', 'The Jay instead of the Osteopath', 'The Jay instead of the Osteopath but more so',
     '3.0'),
    ('452', 'The Mule for Counsellor', 'The Mule for Counsellor but more so', '3.0'),
    ('473', 'The Zebra instead of the Tyre Fitter',
     'The Zebra instead of the Tyre Fitter but more so', '2.0'),
    ('148', 'The Sockeye salmon', 'The Sockeye salmon but more so', '3.0'),
    ('567', 'The Dingo for Toy Maker', 'The Dingo for Toy Maker but more so', '3.0'),
    ('131', 'The Barnacle', 'The Barnacle but more so', '3.0'),
    ('283', 'The Mockingbird exploring the Zoo Keeper',
     'The Mockingbird exploring the Zoo Keeper but more so', '3.0'),
    ('584', 'The Perch instead of the Chicken Chaser',
     'The Perch instead of the Chicken Chaser but more so', '4.0'),
    ('141', 'The Flamingo training for the Tattooist',
     'The Flamingo training for the Tattooist but more so', '3.0'),
    ('404', 'The Turtle exploring the Paediatrician',
     'The Turtle exploring the Paediatrician but more so', '1.0'),
    ('466', 'Basic the  Smelt', 'Basic the  Smelt but more so', '4.0'),
    ('456', 'Inspecting the  Bear', 'Inspecting the  Bear but more so', '4.0'),
    ('164', 'The Cape buffalo', 'The Cape buffalo but more so', '4.0'),
    ('161', 'The Boar as symbol for the Storeman',
     'The Boar as symbol for the Storeman but more so', '2.0'),
    ('238', 'The Gopher killing the Speech Therapist',
     'The Gopher killing the Speech Therapist but more so', '3.0'),
    ('155', 'Inspecting the  Porpoise killing the Caulker',
     'Inspecting the  Porpoise killing the Caulker but more so', '3.0'),
    ('182', 'The Aardwolf', 'The Aardwolf but more so', '4.0'),
    ('249', 'The Cephalopod', 'The Cephalopod but more so', '4.0'),
    ('459', 'Introduction to the  Vampire squid',
     'Introduction to the  Vampire squid but more so', '3.0'),
    ('530', 'Deconstruction of  the  Anglerfish',
     'Deconstruction of  the  Anglerfish but more so', '4.0'),
    ('402', 'Introduction to the  Wren and their Blinds Installer',
     'Introduction to the  Wren and their Blinds Installer but more so', '3.0'),
    ('237', 'Theoretical Topics in the  Fly killing the Hospital Manager',
     'Theoretical Topics in the  Fly killing the Hospital Manager but more so', '3.0'),
    ('108', 'The Wildfowl and the Groom', 'The Wildfowl and the Groom but more so', '3.0'),
    ('552', 'The Aardvark training for the Accounts Manager',
     'The Aardvark training for the Accounts Manager but more so', '4.0'),
    ('378', 'The Swift exploring the Caulker', 'The Swift exploring the Caulker but more so',
     '4.0'),
    ('339', 'Inspecting the  Peafowl and the Medical Assistant',
     'Inspecting the  Peafowl and the Medical Assistant but more so', '4.0'),
    ('308', 'Composition of the  Smelt killing the Grocer',
     'Composition of the  Smelt killing the Grocer but more so', '3.0'),
    ('385', 'Historical Antecendents of the  Tahr',
     'Historical Antecendents of the  Tahr but more so', '4.0'),
    ('223', 'The Lion and their TV Editor', 'The Lion and their TV Editor but more so', '3.0'),
    ('242', 'The Chimpanzee as Trainee Manager', 'The Chimpanzee as Trainee Manager but more so',
     '3.0'),
    ('482', 'The Right whale', 'The Right whale but more so', '3.0'),
    ('319', 'Introduction to the  Rabbit as symbol for the Maintenance Fitter',
     'Introduction to the  Rabbit as symbol for the Maintenance Fitter but more so', '1.0'),
    ('497', 'The Chameleon instead of the Cable TV Installer',
     'The Chameleon instead of the Cable TV Installer but more so', '4.0'),
    ('353', 'The Water buffalo and their Plant Fitter',
     'The Water buffalo and their Plant Fitter but more so', '3.0'),
    ('160', 'Post-structural analysis of the  Perch exploring the Hairdresser',
     'Post-structural analysis of the  Perch exploring the Hairdresser but more so', '4.0'),
    ('312', 'A Theory of the  Xerinae', 'A Theory of the  Xerinae but more so', '1.0'),
    ('347', 'The Domestic pigeon instead of the Immigration Officer',
     'The Domestic pigeon instead of the Immigration Officer but more so', '4.0'),
    ('374', 'The Constrictor', 'The Constrictor but more so', '4.0'),
    ('596', 'Laboratory:  the  Moose', 'Laboratory:  the  Moose but more so', '4.0'),
    ('453', 'The Seahorse for Hop Merchant', 'The Seahorse for Hop Merchant but more so', '3.0'),
    ('444', 'Lecture Topics in the  Weasel', 'Lecture Topics in the  Weasel but more so', '5.0'),
    ('527', 'Deconstruction of  the  Duck breeds',
     'Deconstruction of  the  Duck breeds but more so', '3.0'),
    ('240', 'Introduction to the  Pig as symbol for the Bill Poster',
     'Introduction to the  Pig as symbol for the Bill Poster but more so', '4.0'),
    ('583', 'The Egret', 'The Egret but more so', '3.0'),
    ('169', 'The Arctic Wolf for Production Hand',
     'The Arctic Wolf for Production Hand but more so', '3.0'),
    ('293', 'The Ox and their Textile Worker', 'The Ox and their Textile Worker but more so',
     '4.0'),
    ('121', 'The Cheetah and their Lock Keeper', 'The Cheetah and their Lock Keeper but more so',
     '3.0'),
    ('578', 'The Fancy rat as Optical Advisor', 'The Fancy rat as Optical Advisor but more so',
     '4.0'),
    ('298', 'The Shark instead of the Transport Controller',
     'The Shark instead of the Transport Controller but more so', '4.0'),
    ('110', 'The Quelea and their Insurance Consultant',
     'The Quelea and their Insurance Consultant but more so', '3.0'),
    ('509', 'The Guan training for the Audit Manager',
     'The Guan training for the Audit Manager but more so', '5.0'),
    ('353', 'The Hookworm and the Slater', 'The Hookworm and the Slater but more so', '4.0'),
    ('302', 'The Crow as symbol for the Revenue Clerk',
     'The Crow as symbol for the Revenue Clerk but more so', '3.0'),
    ('189', 'Advanced Aspects in the  Moose exploring the Trinity House Pilot',
     'Advanced Aspects in the  Moose exploring the Trinity House Pilot but more so', '4.0'),
    ('152', 'Lecture Topics in the  Turtle', 'Lecture Topics in the  Turtle but more so', '4.0'),
    ('566', 'The Woodpecker instead of the Medical Assistant',
     'The Woodpecker instead of the Medical Assistant but more so', '4.0'),
    ('555', 'The Scorpion instead of the Research Technician',
     'The Scorpion instead of the Research Technician but more so', '4.0'),
    ('318', 'Historical Antecendents of the  Newt',
     'Historical Antecendents of the  Newt but more so', '3.0'),
    ('543', 'Basic the  Domestic duck', 'Basic the  Domestic duck but more so', '3.0'),
    ('224', 'A Theory of the  Anaconda', 'A Theory of the  Anaconda but more so', '1.0'),
    ('525', 'The Skink as Barrister', 'The Skink as Barrister but more so', '3.0'),
    ('388', 'The Camel', 'The Camel but more so', '4.0'),
    ('591', 'Historical Antecendents of the  Snail',
     'Historical Antecendents of the  Snail but more so', '3.0'),
    ('449', 'Lecture Topics in the  Starfish', 'Lecture Topics in the  Starfish but more so',
     '5.0'),
    ('118', 'The Basilisk as symbol for the Aircraft Designer',
     'The Basilisk as symbol for the Aircraft Designer but more so', '3.0'),
    ('283', 'Advanced Aspects in the  Domestic goose training for the Cleric',
     'Advanced Aspects in the  Domestic goose training for the Cleric but more so', '3.0'),
    ('587', 'The Dingo instead of the General Practitioner',
     'The Dingo instead of the General Practitioner but more so', '4.0'),
    ('588', 'The Loon', 'The Loon but more so', '3.0'),
    ('493', 'The Capybara', 'The Capybara but more so', '4.0'),
    ('262', 'The Reindeer', 'The Reindeer but more so', '3.0'),
    ('158', 'The Siamese fighting fish', 'The Siamese fighting fish but more so', '1.0'),
    ('503', 'The Dormouse as symbol for the Guest House Proprietor',
     'The Dormouse as symbol for the Guest House Proprietor but more so', '3.0'),
    ('229', 'The Wildcat as symbol for the Miner',
     'The Wildcat as symbol for the Miner but more so', '5.0'),
    ('526', 'The Mongoose and the Chartered', 'The Mongoose and the Chartered but more so',
     '3.0'),
    ('387', 'The Marmot for Palaeontologist', 'The Marmot for Palaeontologist but more so',
     '3.0'),
    ('482', 'Lecture Topics in the  Lamprey and their Shop Manager',
     'Lecture Topics in the  Lamprey and their Shop Manager but more so', '4.0'),
    ('214', 'The Chameleon as Patent Agent', 'The Chameleon as Patent Agent but more so', '1.0'),
    ('328', 'The Society finch', 'The Society finch but more so', '3.0'),
    ('448', 'Survey on the  Camel', 'Survey on the  Camel but more so', '3.0'),
    ('566', 'The Cattle and their Porter', 'The Cattle and their Porter but more so', '3.0'),
    ('145', 'The Domestic Bactrian camel', 'The Domestic Bactrian camel but more so', '2.0'),
    ('181', 'The Bird killing the Chartered', 'The Bird killing the Chartered but more so',
     '4.0'),
    ('488', 'The Monkey', 'The Monkey but more so', '3.0'),
    ('273', 'The Art of the  Gecko', 'The Art of the  Gecko but more so', '4.0'),
    ('402', 'The Marmot', 'The Marmot but more so', '5.0'),
    ('547', 'The Rooster', 'The Rooster but more so', '5.0'),
    ('577', 'The Thrush as symbol for the Casual Worker',
     'The Thrush as symbol for the Casual Worker but more so', '5.0'),
    ('244', 'The Yellow perch', 'The Yellow perch but more so', '1.0'),
    ('482', 'The Scorpion', 'The Scorpion but more so', '1.0'),
    ('272', 'The Ground sloth', 'The Ground sloth but more so', '3.0'),
    ('365', 'The Chinchilla instead of the Violinist',
     'The Chinchilla instead of the Violinist but more so', '4.0'),
    ('205', 'The Goldfish killing the Taxi Controller',
     'The Goldfish killing the Taxi Controller but more so', '5.0'),
    ('465', 'The Termite and their Maintenance Fitter',
     'The Termite and their Maintenance Fitter but more so', '3.0'),
    ('452', 'The Quail', 'The Quail but more so', '3.0'),
    ('526', 'The Toad', 'The Toad but more so', '2.0'),
    ('298', 'The Booby as symbol for the Advertising Agent',
     'The Booby as symbol for the Advertising Agent but more so', '5.0'),
    ('309', 'The Reptile for Cable TV Installer',
     'The Reptile for Cable TV Installer but more so', '3.0'),
    ('516', 'The Aardwolf', 'The Aardwolf but more so', '4.0'),
    ('326', 'The Sawfish as Biologist', 'The Sawfish as Biologist but more so', '4.0'),
    ('368', 'The Chicken as Saw Miller', 'The Chicken as Saw Miller but more so', '4.0'),
    ('480', 'Problems in the  Orangutan', 'Problems in the  Orangutan but more so', '1.0'),
    ('372', 'The Sailfish exploring the Aerial Erector',
     'The Sailfish exploring the Aerial Erector but more so', '2.0'),
    ('501', 'The Jay and the Local Government', 'The Jay and the Local Government but more so',
     '3.0'),
)


def randobj(objs):
    return objs.objects.all()[randint(0, objs.objects.count() - 1)]


error_count = 0
for (cn, t, d, cr) in specs[:to_generate]:
    m = randobj(Major)
    c = Course(major=m, catalog_number=cn, title=t, description=d, credits_earned=cr)
    try:
        c.save()
    except Exception:
        error_count = error_count + 1
        print(f'ERROR: Unable to save {m}-{cn} {t} [m={m},catalog_number={cn}, ' +
              f'title="{t}", description="{d}", credits_earned={cr}]')
    else:
        print(f'create course {m}-{cn} {t}')

if error_count:
    print(f'ERROR: {error_count} errors occurred')
