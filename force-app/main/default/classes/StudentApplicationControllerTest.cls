@IsTest
private class StudentApplicationControllerTest {

    @TestSetup
    static void setupTestData() {
        Lead testLead = new Lead(
            FirstName = 'John',
            LastName = 'Doe',
            Email = 'john.doe@example.com',
            Phone = '555-0199',
            Company = 'Student Application'
        );
        insert testLead;

        Contact testContact = new Contact(
            FirstName = 'Jane',
            LastName = 'Smith',
            Email = 'jane.smith@example.com',
            Phone = '555-0188'
        );
        insert testContact;
    }

    @IsTest
    static void testSubmitApplicationSuccess() {
        Test.startTest();
        String resultId = StudentApplicationController.submitApplication(
            'Alice',
            'Johnson',
            'alice.johnson@example.com',
            '555-0177',
            'Higher Education'
        );
        Test.stopTest();

        System.assertNotEquals(null, resultId, 'Application record ID should not be null after submission.');
        Lead createdLead = [SELECT Id, FirstName, LastName, Email FROM Lead WHERE Id = :resultId LIMIT 1];
        System.assertEquals('Alice', createdLead.FirstName, 'First name should match.');
        System.assertEquals('Johnson', createdLead.LastName, 'Last name should match.');
        System.assertEquals('alice.johnson@example.com', createdLead.Email, 'Email should match.');
    }

    @IsTest
    static void testGetStudentApplications() {
        Test.startTest();
        List<Lead> leads = StudentApplicationController.getStudentApplications();
        Test.stopTest();

        System.assertNotEquals(null, leads, 'Returned list should not be null.');
        System.assert(leads.size() > 0, 'Returned list should contain test records.');
    }

    @IsTest
    static void testGetApplicationById() {
        Lead existingLead = [SELECT Id FROM Lead LIMIT 1];

        Test.startTest();
        Lead result = StudentApplicationController.getApplicationById(existingLead.Id);
        Test.stopTest();

        System.assertNotEquals(null, result, 'Application lead should be retrieved.');
        System.assertEquals(existingLead.Id, result.Id, 'Retrieved Lead ID should match.');
    }

    @IsTest
    static void testSubmitApplicationException() {
        Boolean exceptionThrown = false;
        Test.startTest();
        try {
            StudentApplicationController.submitApplication('', '', '', '', '');
        } catch (AuraHandledException e) {
            exceptionThrown = true;
        } catch (Exception e) {
            exceptionThrown = true;
        }
        Test.stopTest();

        System.assert(exceptionThrown, 'An exception should be thrown when invalid parameters are provided.');
    }
}