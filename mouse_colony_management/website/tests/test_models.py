from django.test import TestCase
from website.models import *
from django.core.exceptions import ValidationError
import datetime as dt

class CageModelTest(TestCase):

    def test_create_cage(self):
        cage = Cage.objects.create(cage_number='C001', cage_type='Standard', location='Room 101')
        self.assertEqual(Cage.objects.count(), 1)
        self.assertEqual(cage.cage_number, 'C001')
        self.assertEqual(str(cage), 'C001')

class UserModelTest(TestCase):

    def test_create_user(self):
        user = User.objects.create_user(
            username='john_doe', 
            first_name="John",
            last_name="Doe",
            email='john_doe@abdn.ac.uk', 
            password='password123',
            role='leader'
        )
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(user.email, 'john_doe@abdn.ac.uk')
        self.assertEqual(user.role, 'leader')

    def test_email_validation(self):
        user = User(username='invalid_user', email='invalid@invalid.com')
        with self.assertRaises(ValidationError):
            user.full_clean()  # This should trigger the clean method and raise a ValidationError

class MouseModelTest(TestCase):

    def setUp(self):
        # Create required related objects (strain, user)
        self.strain = Strain.objects.create(name='C57BL/6')
        self.user = User.objects.create_user(username='mouse_keeper', first_name='John', last_name='Doe', email='keeper@abdn.ac.uk', password='pass123', role='leader')

    def test_create_mouse(self):
        mouse = Mouse.objects.create(
            strain=self.strain,
            tube_id=101,
            dob=dt.date(2023, 1, 1),
            sex='M',
            state='alive',
            mouse_keeper=self.user
        )
        self.assertEqual(Mouse.objects.count(), 1)
        self.assertEqual(mouse.state, 'alive')
        self.assertEqual(str(mouse), f"Mouse {mouse.mouse_id} - {self.strain} - Tube 101")

    def test_mouse_ancestors_descendants(self):
        mother = Mouse.objects.create(strain=self.strain, tube_id=1, dob=dt.date(2020, 1, 1), sex='F', state='alive', mouse_keeper=self.user)
        father = Mouse.objects.create(strain=self.strain, tube_id=2, dob=dt.date(2020, 1, 1), sex='M', state='alive', mouse_keeper=self.user)
        child = Mouse.objects.create(strain=self.strain, tube_id=3, dob=dt.date(2023, 1, 1), sex='M', state='alive', mother=mother, father=father, mouse_keeper=self.user)

        self.assertIn(mother, child.get_ancestors())
        self.assertIn(father, child.get_ancestors())
        self.assertIn(child, mother.get_descendants())
        self.assertIn(child, father.get_descendants())

class RequestModelTest(TestCase):

    def setUp(self):
        self.strain = Strain.objects.create(name='C57BL/6')
        self.user = User.objects.create_user(username='requester', email='requester@abdn.ac.uk', password='pass123')
        self.cage = Cage.objects.create(cage_number='C001', cage_type='Breeding', location='Room 101')
        self.mouse_male = Mouse.objects.create(strain=self.strain, tube_id=101, dob=dt.date(2023, 1, 1), sex='M', state='alive', mouse_keeper=self.user)
        self.mouse_female = Mouse.objects.create(strain=self.strain, tube_id=102, dob=dt.date(2023, 1, 1), sex='F', state='alive', mouse_keeper=self.user)

    def test_breeding_request(self):
        # Valid breeding request
        request = Request.objects.create(
            requester=self.user,
            mouse=self.mouse_male,
            second_mouse=self.mouse_female,
            cage=self.cage,
            request_type='breed'
        )
        request.full_clean()  # Should pass validation
        self.assertEqual(Request.objects.count(), 1)

    def test_invalid_breeding_request(self):
        # Breeding request with same-sex mice
        request = Request(
            requester=self.user,
            mouse=self.mouse_male,
            second_mouse=self.mouse_male,  # Same sex
            cage=self.cage,
            request_type='breed'
        )
        with self.assertRaises(ValidationError):
            request.full_clean()

    def test_culling_request(self):
        # Valid culling request
        cull_request = Request.objects.create(
            requester=self.user,
            mouse=self.mouse_male,
            request_type='cull'
        )
        cull_request.full_clean()  # Should pass validation
        self.assertEqual(Request.objects.count(), 1)

    def test_invalid_culling_request(self):
        # Culling request with a second mouse (shouldn't have one)
        cull_request = Request(
            requester=self.user,
            mouse=self.mouse_male,
            second_mouse=self.mouse_female,
            request_type='cull'
        )
        with self.assertRaises(ValidationError):
            cull_request.full_clean()

class BreedModelTest(TestCase):

    def setUp(self):
        self.strain = Strain.objects.create(name='C57BL/6')
        self.cage = Cage.objects.create(cage_number='C001', cage_type='Breeding', location='Room 101')
        self.male = Mouse.objects.create(strain=self.strain, tube_id=101, dob=dt.date(2023, 1, 1), sex='M', state='alive')
        self.female = Mouse.objects.create(strain=self.strain, tube_id=102, dob=dt.date(2023, 1, 1), sex='F', state='alive')

    def test_breed_creation(self):
        breed = Breed.objects.create(male=self.male, female=self.female, cage=self.cage)
        self.assertEqual(Breed.objects.count(), 1)
        self.assertEqual(str(breed), f"Breeding {self.male.mouse_id} x {self.female.mouse_id}")
        
    def test_end_breeding(self):
        breed = Breed.objects.create(male=self.male, female=self.female, cage=self.cage)
        breed.end_breeding()
        self.assertIsNotNone(breed.end_date)
        self.assertEqual(self.male.state, 'alive')
        self.assertEqual(self.female.state, 'alive')

class StrainModelTest(TestCase):

    def test_create_strain(self):
        strain = Strain.objects.create(name='C57BL/6')
        self.assertEqual(Strain.objects.count(), 1)
        self.assertEqual(str(strain), 'C57BL/6')


class GenotypePhenotypeModelTest(TestCase):

    def setUp(self):
        self.strain = Strain.objects.create(name='C57BL/6')
        self.mouse = Mouse.objects.create(strain=self.strain, tube_id=101, dob=dt.date(2023, 1, 1), sex='M', state='alive')

    def test_create_genotype(self):
        genotype = Genotype.objects.create(
            mouse=self.mouse,
            gene='p53',
            allele_1='A',
            allele_2='B'
        )
        self.assertEqual(Genotype.objects.count(), 1)
        self.assertEqual(str(genotype), f"{self.mouse.mouse_id} - p53: A/B")

    def test_create_phenotype(self):
        phenotype = Phenotype.objects.create(
            mouse=self.mouse,
            characteristic='Coat Color',
            description='Black'
        )
        self.assertEqual(Phenotype.objects.count(), 1)
        self.assertEqual(str(phenotype), f"{self.mouse.mouse_id} - Coat Color: Black")