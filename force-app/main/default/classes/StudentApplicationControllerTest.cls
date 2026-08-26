@IsTest
private class StudentApplicationControllerTest {

    @TestSetup
    static void setupTestData() {
        // Create an Account to act as an Educational Institution
        Account institutionAccount = new Account(
            Name = 'Apex University'
        );
        insert institutionAccount;

        // Create a Student Contact
        Contact studentContact = new Contact(
            FirstName = 'Jane',
            LastName = 'Doe',
            Email = 'jane.doe@example.com',
            Phone = '555-0199',
            AccountId = institutionAccount.Id
        );
        insert studentContact;

        // Create an existing Tuition Payment/Opportunity
        Opportunity tuitionRecord = new Opportunity(
            Name = 'Jane Doe - Fall 2025 Tuition',
            AccountId = institutionAccount.Id,
            StageName = 'Prospecting',
            CloseDate = Date.today().addDays(30),
            Amount = 5000.00
        );
        insert tuitionRecord;
    }

    @IsTest
    static void testSubmitApplicationSuccess() {
        Test.startTest();
        Contact resultContact = StudentApplicationController.submitStudentApplication(
            'John',
            'Smith',
            'john.smith@example.com',
            '555-0144',
            'Computer Science',
            4500.00
        );
        Test.stopTest();

        System.assertNotEquals(null, resultContact, 'The returned student contact should not be null.');
        System.assertNotEquals(null, resultContact.Id, 'The contact should have a valid Salesforce record ID.');

        Contact insertedContact = [
            SELECT Id, FirstName, LastName, Email, Phone 
            FROM Contact 
            WHERE Id = :resultContact.Id
        ];
        System.assertEquals('John', insertedContact.FirstName, 'First name should match input.');
        System.assertEquals('Smith', insertedContact.LastName, 'Last name should match input.');
        System.assertEquals('john.smith@example.com', insertedContact.Email, 'Email should match input.');
    }

    @IsTest
    static void testSubmitApplicationMissingRequiredFields() {
        Boolean exceptionThrown = false;

        Test.startTest();
        try {
            StudentApplicationController.submitStudentApplication(
                '',
                '',
                'invalid-email',
                '',
                '',
                null
            );
        } catch (AuraHandledException e) {
            exceptionThrown = true;
        } catch (Exception e) {
            exceptionThrown = true;
        }
        Test.stopTest();

        System.assertEquals(true, exceptionThrown, 'An exception should be thrown when required fields are missing.');
    }

    @IsTest
    static void testGetStudentDetailsSuccess() {
        Contact existingContact = [SELECT Id, Email FROM Contact WHERE Email = 'jane.doe@example.com' LIMIT 1];

        Test.startTest();
        Contact retrievedContact = StudentApplicationController.getStudentDetails(existingContact.Id);
        Test.stopTest();

        System.assertNotEquals(null, retrievedContact, 'Student details should be successfully retrieved.');
        System.assertEquals('Jane', retrievedContact.FirstName, 'First name should match existing record.');
        System.assertEquals('Doe', retrievedContact.LastName, 'Last name should match existing record.');
    }

    @IsTest
    static void testGetStudentDetailsInvalidId() {
        Id fakeContactId = '003000000000000AAA';
        Boolean exceptionThrown = false;

        Test.startTest();
        try {
            StudentApplicationController.getStudentDetails(fakeContactId);
        } catch (AuraHandledException e) {
            exceptionThrown = true;
        } catch (Exception e) {
            exceptionThrown = true;
        }
        Test.stopTest();

        System.assertEquals(true, exceptionThrown, 'An exception should be thrown when querying a non-existent student record.');
    }

    @IsTest
    static void testProcessTuitionPaymentSuccess() {
        Contact studentContact = [SELECT Id FROM Contact WHERE Email = 'jane.doe@example.com' LIMIT 1];
        Opportunity tuitionRecord = [SELECT Id, StageName, Amount FROM Opportunity WHERE StageName = 'Prospecting' LIMIT 1];

        Test.startTest();
        Opportunity updatedTuition = StudentApplicationController.processTuitionPayment(
            tuitionRecord.Id,
            studentContact.Id,
            5000.00,
            'Credit Card'
        );
        Test.stopTest();

        System.assertNotEquals(null, updatedTuition, 'The processed tuition opportunity should not be null.');
        
        Opportunity refreshedRecord = [
            SELECT Id, StageName, Amount 
            FROM Opportunity 
            WHERE Id = :tuitionRecord.Id
        ];
        System.assertEquals('Closed Won', refreshedRecord.StageName, 'Opportunity stage should be updated to Closed Won after successful payment.');
    }

    @IsTest
    static void testProcessTuitionPaymentInvalidAmount() {
        Contact studentContact = [SELECT Id FROM Contact WHERE Email = 'jane.doe@example.com' LIMIT 1];
        Opportunity tuitionRecord = [SELECT Id FROM Opportunity WHERE StageName = 'Prospecting' LIMIT 1];
        Boolean exceptionThrown = false;

        Test.startTest();
        try {
            StudentApplicationController.processTuitionPayment(
                tuitionRecord.Id,
                studentContact.Id,
                -100.00,
                'Credit Card'
            );
        } catch (AuraHandledException e) {
            exceptionThrown = true;
        } catch (Exception e) {
            exceptionThrown = true;
        }
        Test.stopTest();

        System.assertEquals(true, exceptionThrown, 'An exception should be thrown when processing payment with non-positive amount.');
    }

    @IsTest
    static void testBulkStudentApplicationCreation() {
        List<Contact> studentBatch = new List<Contact>();
        for (Integer i = 0; i < 20; i++) {
            studentBatch.add(new Contact(
                FirstName = 'Student',
                LastName = 'Batch' + i,
                Email = 'student.batch' + i + '@example.com',
                Phone = '555-01' + (i < 10 ? '0' + i : String.valueOf(i))
            ));
        }

        Test.startTest();
        insert studentBatch;
        Test.stopTest();

        List<Contact> insertedList = [SELECT Id FROM Contact WHERE LastName LIKE 'Batch%'];
        System.assertEquals(20, insertedList.size(), 'Bulk student records should be successfully inserted without hitting governor limits.');
    }
}