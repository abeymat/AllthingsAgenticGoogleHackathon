@IsTest
private class StudentApplicationControllerTest {

    @TestSetup
    static void setupData() {
        List<Contact> contacts = new List<Contact>();
        contacts.add(new Contact(
            FirstName = 'Alice',
            LastName = 'Smith',
            Email = 'alice.smith@example.com',
            Phone = '555-0101',
            Title = 'Student Applicant'
        ));
        contacts.add(new Contact(
            FirstName = 'Bob',
            LastName = 'Johnson',
            Email = 'bob.johnson@example.com',
            Phone = '555-0102',
            Title = 'Student Applicant'
        ));
        insert contacts;
    }

    @IsTest
    static void testSubmitNewApplicationSuccess() {
        StudentApplicationController.ApplicationRequest req = new StudentApplicationController.ApplicationRequest();
        req.firstName = 'Charlie';
        req.lastName = 'Brown';
        req.email = 'charlie.brown@example.com';
        req.phone = '555-0103';
        req.title = 'Prospective Student';
        req.description = 'Interested in Computer Science program.';

        Test.startTest();
        Contact result = StudentApplicationController.submitApplication(req);
        Test.stopTest();

        System.assertNotEquals(null, result.Id, 'Contact ID should not be null after insertion.');
        System.assertEquals('Charlie', result.FirstName, 'First name should match.');
        System.assertEquals('charlie.brown@example.com', result.Email, 'Email should match.');
    }

    @IsTest
    static void testUpdateExistingApplication() {
        StudentApplicationController.ApplicationRequest req = new StudentApplicationController.ApplicationRequest();
        req.firstName = 'Alice';
        req.lastName = 'Smith Updated';
        req.email = 'alice.smith@example.com';
        req.phone = '555-9999';

        Test.startTest();
        Contact result = StudentApplicationController.submitApplication(req);
        Test.stopTest();

        System.assertNotEquals(null, result.Id, 'Contact ID should be returned.');
        System.assertEquals('Smith Updated', result.LastName, 'Last name should be updated.');
    }

    @IsTest
    static void testSubmitApplicationValidationNullRequest() {
        Boolean exceptionThrown = false;
        Test.startTest();
        try {
            StudentApplicationController.submitApplication(null);
        } catch (AuraHandledException ex) {
            exceptionThrown = true;
        }
        Test.stopTest();

        System.assertEquals(true, exceptionThrown, 'AuraHandledException should be thrown for null request.');
    }

    @IsTest
    static void testSubmitApplicationValidationMissingLastName() {
        StudentApplicationController.ApplicationRequest req = new StudentApplicationController.ApplicationRequest();
        req.email = 'test@example.com';

        Boolean exceptionThrown = false;
        Test.startTest();
        try {
            StudentApplicationController.submitApplication(req);
        } catch (AuraHandledException ex) {
            exceptionThrown = true;
        }
        Test.stopTest();

        System.assertEquals(true, exceptionThrown, 'AuraHandledException should be thrown for missing last name.');
    }

    @IsTest
    static void testGetRecentApplications() {
        Test.startTest();
        List<Contact> results = StudentApplicationController.getRecentApplications();
        Test.stopTest();

        System.assert(results.size() >= 2, 'Should return at least the setup contacts.');
    }

    @IsTest
    static void testSearchApplications() {
        Test.startTest();
        List<Contact> results = StudentApplicationController.searchApplications('Alice');
        List<Contact> emptySearch = StudentApplicationController.searchApplications('');
        Test.stopTest();

        System.assertEquals(1, results.size(), 'Should find 1 contact for Alice.');
        System.assertEquals('Alice', results[0].FirstName, 'First name should be Alice.');
        System.assert(emptySearch.size() >= 2, 'Empty search should return recent applications.');
    }
}