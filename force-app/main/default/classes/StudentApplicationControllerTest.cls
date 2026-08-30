@IsTest
private class StudentApplicationControllerTest {

    @TestSetup
    static void setupTestData() {
        Account testAccount = new Account(
            Name = 'Test Academic Institution'
        );
        insert testAccount;

        Contact testStudent = new Contact(
            FirstName = 'Jane',
            LastName = 'Doe',
            Email = 'jane.doe@example.com',
            Phone = '555-0199',
            AccountId = testAccount.Id
        );
        insert testStudent;

        Opportunity testTuitionApp = new Opportunity(
            Name = 'Jane Doe - Fall Semester Tuition',
            StageName = 'Prospecting',
            CloseDate = Date.today().addDays(30),
            Amount = 5000.00,
            AccountId = testAccount.Id
        );
        insert testTuitionApp;
    }

    @IsTest
    static void testGetStudentApplications() {
        Contact student = [SELECT Id FROM Contact WHERE Email = 'jane.doe@example.com' LIMIT 1];

        Test.startTest();
        List<Opportunity> applications = StudentApplicationController.getStudentApplications(student.Id);
        Test.stopTest();

        System.assertNotEquals(null, applications, 'Applications list should not be null');
        System.assertEquals(1, applications.size(), 'Expected 1 application record returned');
    }

    @IsTest
    static void testSubmitApplication() {
        Test.startTest();
        Id newAppId = StudentApplicationController.submitApplication(
            'John',
            'Smith',
            'john.smith@example.com',
            '555-0123',
            2500.00
        );
        Test.stopTest();

        System.assertNotEquals(null, newAppId, 'Created record Id should not be null');
        Contact createdStudent = [SELECT Id, FirstName, LastName FROM Contact WHERE Email = 'john.smith@example.com' LIMIT 1];
        System.assertEquals('John', createdStudent.FirstName, 'Student first name should match');
        System.assertEquals('Smith', createdStudent.LastName, 'Student last name should match');
    }

    @IsTest
    static void testProcessTuitionPayment() {
        Opportunity app = [SELECT Id, Amount FROM Opportunity LIMIT 1];

        Test.startTest();
        Boolean isSuccess = StudentApplicationController.processPayment(app.Id, app.Amount);
        Test.stopTest();

        System.assertEquals(true, isSuccess, 'Payment execution should report success');
        Opportunity updatedApp = [SELECT Id, StageName FROM Opportunity WHERE Id = :app.Id];
        System.assertEquals('Closed Won', updatedApp.StageName, 'Status should update to Closed Won post-payment');
    }

    @IsTest
    static void testProcessPaymentNullIdException() {
        Boolean exceptionThrown = false;

        Test.startTest();
        try {
            StudentApplicationController.processPayment(null, 500.00);
        } catch (Exception ex) {
            exceptionThrown = true;
            System.assertNotEquals(null, ex.getMessage(), 'Exception message should be populated');
        }
        Test.stopTest();

        System.assertEquals(true, exceptionThrown, 'An exception should be thrown for null application ID');
    }
}