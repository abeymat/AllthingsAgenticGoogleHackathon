@isTest
public class StudentApplicationControllerTest {

    @isTest
    static void testSubmitApplicationSuccess() {
        StudentApplicationController.ApplicationWrapper app = new StudentApplicationController.ApplicationWrapper();
        app.firstName = 'Jane';
        app.lastName = 'Doe';
        app.email = 'jane.doe@university.edu';
        app.phone = '555-0199';
        app.program = 'Computer Science';
        app.term = 'Fall 2026';

        Test.startTest();
        Id leadId = StudentApplicationController.submitApplication(app);
        Test.stopTest();

        System.assertNotEquals(null, leadId, 'Lead ID should not be null');
        Lead createdLead = [SELECT Id, FirstName, LastName, Email FROM Lead WHERE Id = :leadId];
        System.assertEquals('Jane', createdLead.FirstName);
    }

    @isTest
    static void testSubmitApplicationValidationFailure() {
        StudentApplicationController.ApplicationWrapper app = new StudentApplicationController.ApplicationWrapper();
        
        Boolean exceptionThrown = false;
        Test.startTest();
        try {
            StudentApplicationController.submitApplication(app);
        } catch (AuraHandledException e) {
            exceptionThrown = true;
        }
        Test.stopTest();

        System.assertEquals(true, exceptionThrown, 'AuraHandledException should be thrown for missing required fields');
    }
}