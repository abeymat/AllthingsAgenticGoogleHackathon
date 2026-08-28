@IsTest
private class StudentApplicationControllerTest {

    @IsTest
    static void testSubmitNewApplicationSuccess() {
        StudentApplicationController.ApplicationWrapper appData = new StudentApplicationController.ApplicationWrapper();
        appData.firstName = 'John';
        appData.lastName = 'Doe';
        appData.email = 'john.doe@example.com';
        appData.phone = '555-0199';
        appData.tuitionAmount = 5500.00;

        Test.startTest();
        Map<String, Object> result = StudentApplicationController.submitApplication(appData);
        Test.stopTest();

        System.assertEquals('SUCCESS', result.get('status'), 'Expected status to be SUCCESS');
        System.assertNotEquals(null, result.get('contactId'), 'Contact ID should not be null');
        System.assertNotEquals(null, result.get('opportunityId'), 'Opportunity ID should not be null');

        List<Contact> contacts = [SELECT Id, Email FROM Contact WHERE Email = 'john.doe@example.com'];
        System.assertEquals(1, contacts.size(), 'One contact record should exist');
    }

    @IsTest
    static void testSubmitExistingContactApplication() {
        Contact existing = new Contact(
            FirstName = 'Jane',
            LastName = 'Smith',
            Email = 'jane.smith@example.com',
            Phone = '111-222-3333'
        );
        insert existing;

        StudentApplicationController.ApplicationWrapper appData = new StudentApplicationController.ApplicationWrapper();
        appData.firstName = 'Jane';
        appData.lastName = 'Smith';
        appData.email = 'jane.smith@example.com';
        appData.phone = '999-888-7777';
        appData.tuitionAmount = 3000.00;

        Test.startTest();
        Map<String, Object> result = StudentApplicationController.submitApplication(appData);
        Test.stopTest();

        System.assertEquals('SUCCESS', result.get('status'), 'Expected status to be SUCCESS');

        Contact updatedContact = [SELECT Phone FROM Contact WHERE Id = :existing.Id];
        System.assertEquals('999-888-7777', updatedContact.Phone, 'Contact phone should be updated');
    }

    @IsTest
    static void testSubmitApplicationMissingRequiredFields() {
        StudentApplicationController.ApplicationWrapper appData = new StudentApplicationController.ApplicationWrapper();
        appData.firstName = 'NoLastName';

        Boolean exceptionThrown = false;
        Test.startTest();
        try {
            StudentApplicationController.submitApplication(appData);
        } catch (AuraHandledException e) {
            exceptionThrown = true;
        }
        Test.stopTest();

        System.assertEquals(true, exceptionThrown, 'Expected AuraHandledException when required fields are missing');
    }

    @IsTest
    static void testGetStudentTuitionApplications() {
        Contact c = new Contact(FirstName = 'Alice', LastName = 'Wonder', Email = 'alice@example.com');
        insert c;

        Opportunity opp = new Opportunity(
            Name = 'Alice Wonder - Tuition Application',
            StageName = 'Prospecting',
            CloseDate = System.today().addDays(10),
            Amount = 4000.00,
            ContactId = c.Id
        );
        insert opp;

        Test.startTest();
        List<Opportunity> opps = StudentApplicationController.getStudentTuitionApplications('alice@example.com');
        List<Opportunity> emptyOpps = StudentApplicationController.getStudentTuitionApplications('');
        Test.stopTest();

        System.assertEquals(1, opps.size(), 'Should find 1 application for student');
        System.assertEquals(0, emptyOpps.size(), 'Should return empty list for blank email');
    }
}