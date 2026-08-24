@IsTest
public class StudentApplicationControllerTest {

    @IsTest
    static void testCreateStudentApplicationSuccess() {
        Test.startTest();
        String contactId = StudentApplicationController.createStudentApplication(
            'John',
            'Doe',
            'john.doe@example.com',
            '555-123-4567',
            'Computer Science',
            'Interested in Fall semester'
        );
        Test.stopTest();

        System.assertNotEquals(null, contactId, 'Contact ID should not be null after insertion.');
        
        Contact insertedContact = [SELECT Id, FirstName, LastName, Email, Phone, Description FROM Contact WHERE Id = :contactId LIMIT 1];
        System.assertEquals('John', insertedContact.FirstName, 'First name should match.');
        System.assertEquals('Doe', insertedContact.LastName, 'Last name should match.');
        System.assertEquals('john.doe@example.com', insertedContact.Email, 'Email should match.');
        System.assert(insertedContact.Description.contains('Computer Science'), 'Description should contain selected program.');
    }

    @IsTest
    static void testCreateStudentApplicationFailure() {
        Boolean exceptionThrown = false;
        Test.startTest();
        try {
            StudentApplicationController.createStudentApplication('John', '', 'john@example.com', '555-1234', 'CS', 'Test');
        } catch (AuraHandledException e) {
            exceptionThrown = true;
        }
        Test.stopTest();

        System.assert(exceptionThrown, 'AuraHandledException should be thrown when Last Name is missing.');
    }
}