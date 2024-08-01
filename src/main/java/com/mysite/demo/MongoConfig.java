package com.mysite.demo;
import com.mongodb.client.MongoClients;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.mongodb.core.MongoTemplate;

@Configuration
public class MongoConfig {

    @Bean
    public MongoTemplate mongoTemplate() {
        return new MongoTemplate(MongoClients.create("mongodb+srv://baejh724:project@dent.tskyj2l.mongodb.net/Hospital?retryWrites=true&w=majority&appName=Dent"), "Hospital");
    }
}